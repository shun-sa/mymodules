import numpy as np
from scipy import optimize as opt
from sklearn import linear_model

class Lasso(linear_model.LinearRegression):
    """
    Implementation of lasso using ADMM.
    The optimization objective for Lasso is::

        ||y - Xw||^2_2 + alpha * ||w||_1

    Parameters
    ----------
    iter_num : int
        The number of ADMM iteration.
    alpha : float
        Regularization parameter.
    rho : float
        Parameters of convergence stability. This considered to be l2 norm regularization parameter.
    omega : float
        Parameters of convergence acceleration.
    solver : default "liblinear"
        Type of solver. See uel here https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize
    verbose : boolean
        Print debug message.

    Attributes
    ----------
    coef_ : array, shape (n_features,) | (n_targets, n_features)
        parameter vector (w in the cost function formula)
    intercept_ : float | array, shape (n_targets,)
        independent term in decision function.
    curve : array, shape(iteration num)
        converge curve list.
    
    Examples
    --------
    >>> import reg
    >>> X=[[0,0], [1, 1], [2, 2]]
    >>> y=[0, 1, 2]
    >>> clf = reg.Lasso()
    >>> clf.fit(X,y)

    >>> print clf.coef_
    [ 0.4  0.4]
    >>> print clf.predict([0.5,0.5])
    0.6
    >>> print clf.score(X,y)
    0.96

    """
    def __init__(self, iter_num=10000, alpha=1., rho=1., omega=1.5, solver="liblinear", verbose=False):
        self.alpha = alpha
        self.iter_num = iter_num
        self.rho = rho
        self.verbose = verbose
        self.omega = omega
        self.solver = solver

    def SoftMax(self, kappa, a):
        a_ = a.copy()
        a_[np.where((a_ <= kappa) & (a_ >= -kappa))] = 0
        a_[np.where(a_ > kappa)] = a_[np.where(a_ > kappa)] - kappa
        a_[np.where(a_ < - kappa)] = a_[np.where(a_ < - kappa)] + kappa
        return a_

    def solveLS(self, y, A, x):
        def residuals(x, y, A):
            error = y - np.dot(A, x)
            return np.dot(error, error.T)

        def gradient(x, y, A):
            AtA = np.dot(A.T, A)
            Aty = np.dot(A.T, y)
            return np.dot(AtA, x) - Aty

        def hessian(x, y, A):
            AtA = np.dot(A.T, A)
            return AtA
        if self.solver == "liblinear":
            return np.linalg.solve(A, y)
        elif self.solver == "Newton-CG":
            optionFlag = {'xtol': 1e-10, 'maxiter': 100, 'disp': False}
            res = opt.minimize(residuals, x, (y, A), method='Newton-CG',
                               jac=gradient, hess=hessian, options=optionFlag)
            return res.x

    def fit(self, A, b, sample_weight=None):
        """Fit linear model with coordinate descent
        Fit is on grid of alphas and best alpha estimated by cross-validation.

        Parameters
        ----------
        X : {array-like}, shape (n_samples, n_features)
            Training data. Pass directly as float64, Fortran-contiguous data
            to avoid unnecessary memory duplication. If y is mono-output,
            X can be sparse.
        y : array-like, shape (n_samples,) or (n_samples, n_targets)
            Target values
        """

        A_ = np.copy(A)
        b_ = np.copy(b)
        n_samples, n_features = A_.shape
        I = np.identity(n_features)
        z = np.zeros(n_features)
        u = np.zeros(n_features)
        x = np.zeros(n_features)
        MAT_ = np.dot(A_.T, A_) + (I * self.rho)
        VEC_ = np.dot(A_.T, b_)

        for iter_ in range(self.iter_num):
            z_ = z
            x = self.solveLS(VEC_ + self.rho * (z - u), MAT_, x)
            x = x * self.omega + z * (1 - self.omega)
            z = self.SoftMax(self.alpha / self.rho, x + u)
            u = u + x - z
            if self.verbose:
                print np.dot(z - z_, z - z_)

        self.coef_ = z
        self.intercept_ = np.average(b_) - np.dot(np.mean(A_, axis=0), z)
        return self

