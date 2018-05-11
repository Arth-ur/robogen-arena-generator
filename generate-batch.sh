#/bin/batch
mkdir -p batch/noise
mkdir -p batch/solid
mkdir -p batch/minecraft
mkdir -p batch/realistic
mkdir -p batch/obstacles

for i in $(seq 1 $1); do
python3 noise.py --width 16 --height 16 --png batch/noise/arena$i.png --size 1.5 --pgm - \
    | python3 makearena.py --output - --input pgm - \
    | tee batch/obstacles/arena$i.txt \
    | python3 render.py --passthrough --texture solid --resolution 1080p - batch/solid/arena$i.png \
    | python3 render.py --passthrough --texture minecraft --resolution 1080p - batch/minecraft/arena$i.png \
    | python3 render.py --texture realistic --resolution 1080p - batch/realistic/arena$i.png
done
