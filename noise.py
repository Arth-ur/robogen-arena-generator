import argparse
from math import floor, sqrt
import random
import sys


class Noise:
    def __init__(self, width=16, height=16, size=2):
        self.width = 16
        self.height = 16
        self.size = size
        self.n = 256
        # permutation of n first integers
        self.P = list(range(0, self.n))
        random.shuffle(self.P)
        # random vectors uniformely distributed on the unit area
        self.G = []
        for _ in range(0, self.n):
            while True:
                v = (random.uniform(-1, 1), random.uniform(-1, 1))
                l2 = v[0]**2+v[1]**2
                if l2 <= 1:
                    l = sqrt(l2)
                    v = (v[0] / l, v[1] / l)
                    self.G.append(v)
                    break

    def cw(self, t):
        """ cubic weighting function """
        if abs(t) < 1:
            return 2*abs(t)**3-3*abs(t)**2+1
        else:
            return 0

    def phi(self, i):
        return self.P[i % self.n]

    def tau(self, ij, xy):
        """ Compute inner product of random gradient and xy """
        g = self.G[self.phi(ij[0] + self.phi(ij[1]))]
        p = g[0]*xy[0]+g[1]*xy[1]
        return p

    def knot(self, ij, xy):
        """ Knot at lattice point (i,j) """
        return self.cw(xy[0])*self.cw(xy[1])*self.tau(ij, xy)

    def val(self, x, y):
        """ Compute value at (x, y) """
        x *= self.size
        y *= self.size
        v = 0
        i = floor(x)
        j = floor(y)
        v += self.knot((i, j), (x-i, y-j))
        i = floor(x)+1
        j = floor(y)
        v += self.knot((i, j), (x-i, y-j))
        i = floor(x)
        j = floor(y)+1
        v += self.knot((i, j), (x-i, y-j))
        i = floor(x)+1
        j = floor(y)+1
        v += self.knot((i, j), (x-i, y-j))
        return 128+floor(v * 128)

def print_data(data, width, height, f):
    """ Write an array to file f """
    f.write('P2\n')
    f.write('{} {}\n'.format(width, height))
    f.write('255\n')
    for Y in range(0, height):
        for X in range(0, width):
            f.write('{} '.format(data[(width-X-1)*height+(height-Y-1)]))
        f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate noise.',
                                     epilog='Noise generation is based on the noise function described in the paper Perlin, K, and Hoffert, E. M., "Hypertexture", Computer Graphics 23, 3 (August 1989).')
    parser.add_argument('--width', type=int, default=16,
                        help='output image width')
    parser.add_argument('--height', type=int, default=16,
                        help='output image height')
    parser.add_argument('--size', type=float, default=2,
                        help='size of noise')
    parser.add_argument('--png', type=str,
                        help='name of png output file')
    parser.add_argument('--pgm', type=str,
                        help='output PGM to file or stdout if -')
    args = parser.parse_args()

    noise = Noise(width=args.width, height=args.height, size=args.size)
    data = []

    for X in range(0, args.width):
        for Y in range(0, args.height):
            # divide by the lattice size
            x = X / args.width
            y = Y / args.height
            pixel = noise.val(x, y)
            data.append(pixel)

    # Flatten the center
    sum = (data[(floor(args.width/2) + 0) * args.height + (floor(args.height/2) + 0)]
           + data[(floor(args.width/2) + 0) *
                  args.height + (floor(args.height/2) - 1)]
           + data[(floor(args.width/2) - 1) *
                  args.height + (floor(args.height/2) + 0)]
           + data[(floor(args.width/2) - 1) *
                  args.height + (floor(args.height/2) - 1)])
    avg = int(sum / 4)
    gain = 0.5
    data[(floor(args.width/2) + 0) * args.height + (floor(args.height/2) + 0)] += int(gain *
                                                                                      (avg - data[(floor(args.width/2) + 0) * args.height + (floor(args.height/2) + 0)]))
    data[(floor(args.width/2) + 0) * args.height + (floor(args.height/2) - 1)] += int(gain *
                                                                                      (avg - data[(floor(args.width/2) + 0) * args.height + (floor(args.height/2) - 1)]))
    data[(floor(args.width/2) - 1) * args.height + (floor(args.height/2) - 1)] += int(gain *
                                                                                      (avg - data[(floor(args.width/2) - 1) * args.height + (floor(args.height/2) - 1)]))
    data[(floor(args.width/2) - 1) * args.height + (floor(args.height/2) + 0)] += int(gain *
                                                                                      (avg - data[(floor(args.width/2) - 1) * args.height + (floor(args.height/2) + 0)]))

    if args.pgm == '-':
        print_data(data[:], args.width, args.height, sys.stdout)
    elif args.pgm is not None:
        with open(args.pgm, 'w') as f:
            print_data(data[:], args.width, args.height, f)

    if args.png is not None:
        from PIL import Image
        image = Image.new('L', (args.width, args.height))
        for X in range(0, args.width):
            for Y in range(0, args.height):
                image.putpixel((X, Y), data.pop())
        image.save(args.png)
