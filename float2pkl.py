#!/usr/bin/env python
import socio
import sys
import st
import os
import argparse
import numpy as np


def getparse():
    # Parse program arguments
    parser = argparse.ArgumentParser(description='plot spectrum')
    parser.add_argument(dest='file_in', metavar='spec_file')
    parser.add_argument('-o', '--out-suffix',
                        metavar='SUFFIX', type=str, default=None)
    parser.add_argument('-s', '--silence', action='store_true',
                        required=False, default=False)
    parser.add_argument('-same', action='store_true',
                        required=False, default=False)
    parser.add_argument('-sl', '--slice', type=str,
                        required=False, default=":,:,:")
    return parser.parse_args()


args = getparse()


if args.out_suffix is None:
    basename = str(os.path.basename(sys.argv[1])).replace(".float", "")
else:
    basename = args.out_suffix.replace(".pkl", "")
if not args.same:
    DIR = str(os.path.dirname(sys.argv[1]))
    if DIR:
        DIR += "/"
    basename = DIR + basename

r = socio.openfloat(args.file_in)
R = r[st.parse2slice(args.slice)]

st.savepickle(basename + ".pkl", R.astype(np.float16))

if not args.silence:
    try:
        wav = r.getWavelengths()
        np.savetxt("wavelength.txt", wav)
        socio.savefig(basename + ".png", R[:, :, 20])
    except:
        Exception("cant get slice %s" % str(R.shape))
