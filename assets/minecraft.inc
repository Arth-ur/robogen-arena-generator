// POV-Ray 3,5 include file "minecraft.inc"

// A ground texture
#declare Ground = texture { uv_mapping
    pigment {
            image_map {
                png "assets/minecraft/ground.png"
                map_type 0
                interpolate 2
            }
        }
    finish { phong 1 }
}

// A pebble texture
#declare Pebble = texture { uv_mapping
    pigment {
            image_map {
                png "assets/minecraft/pebble.png"
                map_type 0
                interpolate 2
            }
        }
    finish { phong 1 }
}

#declare Rock = texture { uv_mapping
    pigment {
            image_map {
                png "assets/minecraft/rock.png"
                map_type 0
                interpolate 2
            }
        }
    finish { phong 1 }
}
