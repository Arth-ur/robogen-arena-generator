#/bin/batch
python3 noise.py --width 16 --height 16 --png $1.noise.png --size 1.5 --pgm - \
    | python3 makearena.py --output - --input pgm - \
    | tee $1.txt \
    | python3 render.py --passthrough --texture solid --resolution 1080p - $1.solid.png \
    | python3 render.py --passthrough --texture minecraft --resolution 1080p - $1.minecraft.png \
    | python3 render.py --texture realistic --resolution 1080p - $1.realistic.png
