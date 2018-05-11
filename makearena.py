import argparse
import math
import sys
import random

try:
    import shapely.geometry
    import shapely.affinity

    class RotatedRect:
        def __init__(self, cx, cy, w, h, angle):
            c = shapely.geometry.box(-w/2.0, -h/2.0, w/2.0, h/2.0)
            rc = shapely.affinity.rotate(c, angle)
            self.trc = shapely.affinity.translate(rc, cx, cy)

        def intersects(self, other):
            return self.trc.intersects(other.trc)

    def is_colliding(a, b):
        A = RotatedRect(a['x'], a['y'], a['sx'], a['sy'], math.radians(a['r']))
        B = RotatedRect(b['x'], b['y'], b['sx'], b['sy'], math.radians(b['r']))
        return A.intersects(B)

except ImportError:
    # shapely is not available, collision detection is not performed
    def is_colliding(a, b): return False

def gen(f, data, args):
    # inverse grescale if needed
    if args.inverse:
        data = [128 - p for p in data]
    # map greyscale to heights
    heights = [p * (args.hrange / 128.0) for p in data]
    # lower to map to minimum
    min_height = min(heights)
    heights = [height - min_height + args.hoffset for height in heights]
    # create 2d heightmap
    heightmap = [heights[offset:offset+args.width]
                 for offset in range(0, args.width*args.height, args.width)]

    # output map
    for i in range(0, args.width):
        for j in range(0, args.height):
            # compute coordinates
            x = i * args.pixelsize - args.width / 2 * args.pixelsize
            y = j * args.pixelsize - args.width / 2 * args.pixelsize
            # retrieve height
            height = heightmap[i][j]
            # print obstacle
            f.write('{x} {y} {sx} {sy} {sz} {d}\n'.format(
                x=x,
                y=y,
                sx=args.pixelsize,
                sy=args.pixelsize,
                sz=height,
                d=0.0  # infinite density
            ))

    # a list of dicts (x, y, z, sx, sy, sz, angle)
    obstacles = []

    # add rocks
    for i in range(0, args.nrocks):
        s = round(random.uniform(0.05, 0.2), 5)
        while True:
            x = round(random.uniform(-args.width/2.0+1,
                                     args.width/2.0-1) * args.pixelsize, 5)
            y = round(random.uniform(-args.height/2.0+1,
                                     args.height/2.0-1) * args.pixelsize, 5)
            # Safe zone
            if abs(x) > 0.3 or abs(y) > 0.3:
                break
        z = max([
            heightmap[int(x / args.pixelsize + args.width / 2.0)
                      ][int(y / args.pixelsize + args.height / 2.0)],
            heightmap[int((x + s) / args.pixelsize + args.width / 2.0)
                      ][int(y / args.pixelsize + args.height / 2.0)],
            heightmap[int((x - s) / args.pixelsize + args.width / 2.0)
                      ][int(y / args.pixelsize + args.height / 2.0)],
            heightmap[int(x / args.pixelsize + args.width / 2.0)
                      ][int((y + s) / args.pixelsize + args.height / 2.0)],
            heightmap[int(x / args.pixelsize + args.width / 2.0)
                      ][int((y + s) / args.pixelsize + args.height / 2.0)],
        ]) + s / 2.0 - 0.1
        # rotation around z axis
        r = round(random.uniform(1, 89), 5)
        # rocks are allowed to collide with other rocks
        # add rock to obstacles list
        obstacles.append(
            {'x': x, 'y': y, 'z': z, 'sx': s, 'sy': s, 'sz': s, 'r': r})
        f.write('{x} {y} {z} {sx} {sy} {sz} {d} 0 0 1 {r}\n'.format(
            x=x,
            y=y,
            z=z,
            sx=s,
            sy=s,
            sz=s,
            d=0.0,
            r=r
        ))

    # add pebbles
    for i in range(0, args.npebbles):
        while True:
            s = round(random.uniform(0.02, 0.05), 5)
            while True:
                # pebbles are generated inside a pixel and at the center of the arena
                xi = random.randint(
                    int(args.pregion*args.width) + 1, int((1-args.pregion)*args.width-1))
                yi = random.randint(
                    int(args.pregion*args.height) + 1, int((1-args.pregion)*args.height-1))
                x = round((xi - args.width/2) * args.pixelsize +
                          random.uniform(-args.pixelsize/2+s, args.pixelsize/2-s), 5)
                y = round((yi - args.height/2) * args.pixelsize +
                          random.uniform(-args.pixelsize/2+s, args.pixelsize/2-s), 5)
                # Safe zone around robot
                if abs(x) > 0.3 or abs(y) > 0.3:
                    break
            z = heightmap[xi][int(yi)] + s / 2.0
            # rotation around z axis
            r = round(random.uniform(1, 89), 5)
            # pebbles are not allowed to collide with rocks or other pebbles
            colliding = False
            for obstacle in obstacles:
                if is_colliding({'x': x, 'y': y, 'z': z, 'sx': s, 'sy': s, 'sz': s, 'r': r}, obstacle):
                    colliding = True
                    break
            if not colliding:
                break

        # add pebbles to obstacles list
        obstacles.append(
            {'x': x, 'y': y, 'z': z, 'sx': s, 'sy': s, 'sz': s, 'r': r})
        f.write('{x} {y} {z} {sx} {sy} {sz} {d} 0 0 1 {r}\n'.format(
            x=x,
            y=y,
            z=z,
            sx=s,
            sy=s,
            sz=s,
            d=args.density,
            r=r
        ))

def read_data(f):
    """
    The PGM format is not totally implemented:
     * only newline are considered whitespaces
     * other...
    It is fully compatible with the output of noise.py
    """
    # check format header
    line = f.readline().strip()
    if line != 'P2':
        print('Error: unsupported file format "{}"'.format(line), file=sys.stderr)
        return None
    line = f.readline().strip()
    width, height = line.split(' ') # TODO: use these values instead of the optional parameters values

    line = f.readline().strip()
    maxval = int(line)              # TODO: normalise grayscale using this value

    data = []
    for line in f:
        data.extend(map(int, line.strip().split(' ')))
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate arenas.')
    parser.add_argument('source', type=str,
                        help='source noise image or - for standard input')

    parser.add_argument('--width', type=float, default=16,
                        help='image region width (png only)')
    parser.add_argument('--height', type=float, default=16,
                        help='image region width (png only)')
    parser.add_argument('-x', type=int, default=0,
                        help='image region top left corner x coordinate (png only)')
    parser.add_argument('-y', type=int, default=0,
                        help='image region top left corner y coordinate (png only)')
    parser.add_argument('-s', '--pixelsize', type=float, dest='pixelsize', default=0.2,
                        help='Size of one pixel in meter (scale)')
    parser.add_argument('--hoffset', type=float, default=0.1,
                        help='height offset')
    parser.add_argument('--hrange', type=float, default=0.4,
                        help='height range')
    parser.add_argument('-i', type=bool, default=False, dest='inverse',
                        help='inverse grayscale')
    parser.add_argument('--nrocks', type=int, default=50,
                        help='Number of rocks')
    parser.add_argument('--npebbles', type=int, default=50,
                        help='Number of pebbles')
    parser.add_argument('--density', type=int, default=1000,
                        help='Density value of a pebble obstacle')
    parser.add_argument('--pregion', type=float, default=0.2,
                        help='The fraction of the arena that is occupied by pebbles')
    parser.add_argument('-o', '--output', type=str, default='-', dest='output',
                        help='Output file or - for standard output')
    parser.add_argument('--input', choices=['png', 'pgm'], default='png',
                        help='Input file type. Only a subset of the PGM format is implemented.')

    args = parser.parse_args()

    if args.input == 'png':
        from PIL import Image
        # convert image to 8-bit grayscale
        img = Image.open(args.source).convert('L')
        # crop image according to args.width and args.height
        img = img.crop((args.x, args.y, args.width +
                        args.x, args.height + args.y))
        # convert image to 2D array
        data = list(img.getdata())
    elif args.input == 'pgm':
        if args.source == '-':
            data = read_data(sys.stdin)
        else:
            with open(args.source, 'r') as f:
                data = read_data(f)

    if args.output == '-':
        gen(sys.stdout, data, args)
    else:
        with open(args.output, 'w') as f:
            gen(f, data, args)
