# vapory overrides the name
py_name = __name__

import argparse
from vapory import *
import sys


def scene(objects, output, width, height, texture):
    camera = Camera('orthographic', 'location', [-3, -6, 7],
                    'right', 'x*image_width/image_height',
                    'angle', 33+height/200,
                    'look_at', [0, 0, 0],
                    'sky', [3/9, 6/9, 0]
                    )
    key_light = LightSource([0, -3, 9], 'color', [1, 1, 1],
                            'spotlight',
                            'radius', 0.001,
                            'point_at', [0, 0, 0])
    fill_light = LightSource([6, 0, 9], 'color', [0.1, 0.1, 0.1],
                             'spotlight',
                             'radius', 1,
                             'point_at', [0, 0, 0])
    back_light = LightSource([3, 6, 0], 'color', [1, 1, 1],
                             'spotlight',
                             'radius', 1,
                             'point_at', [0, 0, 0])
    objects.append(key_light)
    objects.append(fill_light)
    objects.append(back_light)
    scene = Scene(camera, objects=objects, included=[
        'textures.inc', 'colors.inc', 'assets/{}.inc'.format(texture)])
    scene.render(output,
                 auto_camera_angle=False,
                 width=width, height=height,
                 antialiasing=0.1)

def read_arena(lines):
    objects = []
    for line in lines:
        tokens = line.split(' ')
        c1 = [-0.5, -0.5, -0.5]
        c2 = [+0.5, +0.5, +0.5]
        if len(tokens) == 6:
            x, y, sx, sy, sz, _ = map(float, tokens)
            objects.append(Box(c1, c2,  Texture('Ground'),
                                'scale', [sx, sy, sz],
                                'translate', [x, y, sz/2]))
        elif len(tokens) == 11:
            x, y, z, sx, sy, sz, d, _, _, _, r = map(float, tokens)
            # use density
            if float(d) == 0.0:
                texture = 'Rock'
            else:
                texture = 'Pebble'
            objects.append(Box(c1, c2,  Texture(texture),
                                'scale', [sx, sy, sz],
                                'rotate', [0, 0, r],
                                'translate', [x, y, z]
                                ))
    return objects


if py_name == '__main__':
    parser = argparse.ArgumentParser(description='Generate image.')

    parser.add_argument('arena', type=str,
                        help='arena file path or - for standard input')
    parser.add_argument('output', type=str,
                        help='Output file')

    parser.add_argument('--resolution', default='240p',
                        choices=['240p', '320p', '480p', '720p', '1080p'],
                        help='Image quality')
    parser.add_argument('--texture', default='minecraft', type=str,
                        help='Texture')
    parser.add_argument('--passthrough', action='store_true',
                        help='output arena file at end of rendering')

    args = parser.parse_args()

    lines = []
    if args.arena == '-':
        lines = sys.stdin.readlines()
    else:
        with open(args.arena, 'r') as f:
            lines = f.readlines()
    objects = read_arena(lines)

    if args.resolution == '1080p':
        width = 1920
        height = 1080
    elif args.resolution == '720p':
        width = 1280
        height = 720
    elif args.resolution == '480p':
        width = 640
        height = 480
    elif args.resolution == '320p':
        width = 480
        height = 320
    elif args.resolution == '240p':
        width = 320
        height = 240

    scene(objects, args.output, width, height, args.texture)
    if args.passthrough:
        for line in lines: sys.stdout.write(line)
