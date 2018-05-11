// POV-Ray 3,5 include file "realistic.inc"

// A ground texture
#declare Ground = texture { uv_mapping
    pigment {
            image_map {
                jpeg "assets/realistic/ground.jpg"
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
                jpeg "assets/realistic/pebble.jpg"
                map_type 0
                interpolate 2
            }
        }
    finish { phong 1 }
}

#declare Rock = texture { uv_mapping
    pigment {
            image_map {
                jpeg "assets/realistic/rock.jpg"
                map_type 0
                interpolate 2
            }
        }
    finish { phong 1 }
}
