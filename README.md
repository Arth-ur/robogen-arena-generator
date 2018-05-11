# Arena generator
Tools for generating robogen arenas. See the `examples` directory for example of
obstacle files and preview images.

## Description
There are three tools: a solid noise generator, an arena generator and a 3D
scene builder. The three tools can be easily piped into each other to generate
the arena and the preview images.

### Noise generator
The noise generator is based on the noise function described in [Perlin, K. &
Hoffert, E. M. (1989). Hypertexture. SIGGRAPH Comput. Graph., 23,
253-262.](http://web.cse.ohio-state.edu/~shen.94/681/Site/Slides_files/p253-perlin.pdf)
The output of the generator is a grayscale image in [PGM
format](http://netpbm.sourceforge.net/doc/pgm.html), a human readable image
format. The PGM file is written to the standard output unless the `--pgm` option
is used.

The width and height in pixels of the generated image can be set using options
`--width` and `--height` respectively. The `--size` option changes the level of
noise. The noise is _softer_ when the size is small.

The `--png` option can be used to save the noise image as a PNG file. This
option will fail if [Pillow](https://github.com/python-pillow/Pillow) is not
available.

Here is an example that generates a 16 pixels by 16 pixels image suitable for
small robogen arenas:
```
$ python3 noise.py --width 16 --height 16 --size 1.5 --png noise.png --pgm -
```

`--pgm -` means that the pgm file should be sent to standard output (this is the
default behaviour). `--png noise.png` creates a PNG file named `noise.png` as
well.

The `noise` directory contains example of noise images.

### Make arena
The `makearena.py` script generates an arena from a source grayscale image. The
algorithm has three steps:
 1. The source image is decoded and converted into an heigt map. The height map
    is used to generate the ground using simple box obstacles. The size of each
    pixel along the x and y axis is set using options `--pixelsize` (or `-s`).
    The `--hrange` set the mapping from grayscale image to height in meters
    `(0,255) -> (0, hrange)`. The `--hoffset` is used to add a small offset
    height to the whole height map. The source image can be inverted using
    option `-i`.
 2. Rocks are infinite density cubes of random sizes, rotations and positions.
    To avoid colliding with the robot, they are not added at the center of the
    arena. The number of rocks is set using option `--nrocks`.
 3. Pebbles are finite density cubes of random sizes, rotations and positions.
    To avoid colliding with the robot, they are not added at the center of the
    arena. The density of the pebbles can be changed using options `--density`.
    To keep pebbles around the center of the arena, one can adjust the
    `--pregion` settings which is the fraction of the arena that is occupied by
    the pebbles. The number of pebbles is set using option `--npebbles`.

If [shapely](https://pypi.org/project/Shapely/) is available, collisions
detection will be performed in order to avoid collision between a pebble and
another pebble, or a pebble and a rock.

The output file is an obstacle text file that can be sent to a file using
`--output` or to standard output if the specified file name is `-`.

The source image can either be a PNG file or a PGM file. The format of the image
must be specified using `--input png` or `--input pgm` respectively. The image
can be read from a file or from standard input if the source image path is set
to `-`. [Pillow](https://github.com/python-pillow/Pillow) must be available to
read a PNG source input image.

The PGM image from the `noise.py` script can be piped directly into the
`makearena.py` script like so:
```
$ python3 noise.py --width 16 --height 16 --png noise.png --size 1.5 --pgm - \
    | python3 makearena.py --output - --input pgm -
```

If the source image is read from a PNG file, one can use the `--width` and
`--height` options to set the dimensions the region of interest; and the `-x`
and `-y` options to set the coordinates of the top left corner of the region of
interset.

### 3D scene builder
The last script `render.py` builds a 3D scene description from an arena file
that is fed to the [Persistence of Vision Ray Tracer
(POV-Ray)](http://www.povray.org/) using the [Vapory binding for
python](https://github.com/Zulko/vapory).

The script requires two parameters: the arena file path and the output file
path. The rendered scene is saved in PNG format. If the arena file path is `-`,
the arena file is read from standard input. Therefore, the output of
`makearena.py` can be piped directly into the `render.py` script like so:
```
$ python3 noise.py --width 16 --height 16 --png noise.png --size 1.5 --pgm - \
    | python3 makearena.py --output - --input pgm - \
    | python3 render.py --passthrough --texture solid --quality 1080p - solid.png
```

The resolution of the rendering can be set using the `--resolution` option.
Available resolutions are: `1080p`, `720p`, `480p`, `320p` and `240p`.

The texture of the ground, rocks and pebbles can be changed using the
`--texture` option. This option simply include the provided texture name in the
scene description. For example, `--texture solid` includes the
`assets/solid.inc` file in the scene description. Three textures are already
provided: `solid` uses only solid colors for the different obstacles,
`minecraft` used UV mapping of minecraft textures and `realistic` uses UV
mapping with a martian ground texture. All textures differentiates the three
elements type (ground, rocks and pebbles) using the z coordinate and the density
of the obstacles.

The `--passthrough` option sends standard input to standard output. This is
useful for piping multiple `render.py` commands using different resolution and
texture settings. Here is an example to generate rendering using the three
available textures:
```
$ python3 noise.py --width 16 --height 16 --png noise.png --size 1.5 --pgm - \
    | python3 makearena.py --output - --input pgm - \
    | python3 render.py --passthrough --texture solid - solid.png \
    | python3 render.py --passthrough --texture minecraft  - minecraft.png \
    | python3 render.py --texture realistic - realistic.png
```

## Front ends
Two front ends are available for common operations.

`generate-single.sh` generates a noise image in PNG format, an obstacle file,
and three 1080p rendering using each of the three available textures. The first
argument of the script must be the prefix of the files to be generated. Example
to generate `/tmp/my-arena.noise.png`, `/tmp/my-arena.txt`, ...
```
$ generate-single.sh /tmp/my-arena
```

`generate-batch.sh` generates a batch of arenas inside `batch` directory. Noise
images are created inside directory `batch/noise`, obstacles files are created
inside directory `batch/obstacles`, ... The first argument of the script must be
the number of arenas to generate. Example for generating ten arenas:
```
$ generate-batch.sh 10
```

## Requirements
 * [python3](https://www.python.org/) is the only required dependency
 * [shapely](https://pypi.org/project/Shapely/) is required for collisions
   detection
 * [Pillow](https://github.com/python-pillow/Pillow)for image processing of
   noise images
 * [POV-Ray](http://www.povray.org/) and the [Vapory binding for
   python](https://github.com/Zulko/vapory) for rendering preview images

The bash scripts `generate-batch.sh` and `generate-single.sh` have to be run
using bash.

## Noise images using Gimp
Noise image must be a png file which is internally converted to a grayscale
image and cropped to a given region. A noise image can be generated using Gimp.
To do so, create a new image and then run the Solid Noise filter. In Gimp
2.8.16, this filter is located in `Filters > Render > Clouds > Solid Noise...`.
Save as a png file. For best results, set detail to 1 and set X size and Y size
to the width and height of the image respectively divided by 32. Uncheck
tileable and turbulent. Hit OK and export the image to PNG file format. The
algorithm used by Gimp follows the [Perlin & Hoffert
paper](http://web.cse.ohio-state.edu/~shen.94/681/Site/Slides_files/p253-perlin.pdf)
as well.
