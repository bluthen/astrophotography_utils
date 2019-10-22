from astropy.io import fits
import sys
import glob
import getopt
import os

fits_fn = sys.argv[1]
pattern = 'GGBR'


def ggbr_to_rggb_reorder(data):
    data1 = data.copy()
    for y in range(len(data)):
        for x in range(len(data[0])):
            if y % 2 == 0:
                if x % 2 == 0:
                    v = data[y + 1][x + 1]  # R
                else:
                    v = data[y][x]  # G2
            else:
                if x % 2 == 0:
                    v = data[y - 1][x]  # G1
                else:
                    v = data[y][x - 1]  # B
            data1[y][x] = v
    return data1


def process(file, workdir, prefix):
    base = os.path.basename(file)
    dirname = os.path.dirname(file)
    pattern = 'RGGB'
    hdul = fits.open(file)
    hdul[0].header['BAYERPAT'] = pattern
    hdul[0].header['XBAYROFF'] = 0
    hdul[0].header['YBAYROFF'] = 0

    hdul[0].header.comments['BAYERPAT'] = 'Bayer color pattern'
    hdul[0].header.comments['XBAYROFF'] = 'X offset of Bayer array'
    hdul[0].header.comments['YBAYROFF'] = 'Y offset of Bayer array'
    newdata = ggbr_to_rggb_reorder(hdul[0].data)
    hdul[0].data = newdata
    if workdir is None:
        workdir = dirname
    new_fn = os.path.join(workdir, (prefix + '_' + base))
    hdul.writeto(new_fn)
    print(new_fn)


def usage():
    print('Usage: %s [options] [fits_files]')
    print('Makes a GGBR bayer pattern into RGGB.')
    print('OPTIONS')
    print('    -h, --help                  This help screen')
    print('    -w dir, --workdir dir       Directory to save files, defaults to location of input file')
    print('    -p prefix, --prefix prefix  Prefix of new file')
    print()


def main():
    workdir = None
    prefix = 'RGGB'
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hw:p:', ['help', 'workdir=', 'prefix='])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-w', '--workdir'):
            workdir = a
        elif o in ('-p', '--prefix'):
            prefix = a
    if len(args) == 0:
        print('ERROR: No fits files specified.')
        sys.exit(3)
    print({'prefix': prefix, 'args': args, 'workdir': workdir})
    files = []
    for f in args:
        files.extend(glob.glob(f))
    for f in files:
        process(f, workdir, prefix)
    print('Done.')


if __name__ == '__main__':
    main()
