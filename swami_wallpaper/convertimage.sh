#!/bin/bash
WP=$1
FNAME=$2

    OUTPUT_DIR="$HOME/.e/e/backgrounds"

    TEMPLATE='
    images { image: "@IMAGE@" USER; }
    collections {
      group {
      name: "e/desktop/background";
      data { item: "style" "4"; item: "noanimation" "1"; }
      max: @WIDTH@ @HEIGHT@;
      parts {
        part {
        name: "bg";
        mouse_events: 0;
        description {
          state: "default" 0.0;
          aspect: @ASPECT@ @ASPECT@;
          aspect_preference: NONE;
          image { normal: "@IMAGE@"; scale_hint: STATIC; }
        }
        }
      }
      }
    }
    '

    OFILE="$OUTPUT_DIR/$FNAME"

    DIMENSION="$(identify -format "%w/%h" "$WP")"

    if [ ! -z "$DIMENSION" ]; then
        WIDTH=$(echo $DIMENSION | cut -d/ -f1)
        HEIGHT=$(echo $DIMENSION | cut -d/ -f2)
        IMAGE="$(echo "$WP" | sed 's/[^[:alnum:]_-]/\\&/g')"

        if [ -z "$HEIGHT" -o "$HEIGHT" = "0" ]; then
            ASPECT="0.0"
        else
            ASPECT=$(echo "scale=9; $DIMENSION" | bc)
        fi
    fi

    printf "%s" "$TEMPLATE" | \
    sed "s/@ASPECT@/$ASPECT/g; s/@WIDTH@/$WIDTH/g; s/@HEIGHT@/$HEIGHT/g; s|@IMAGE@|$IMAGE|g" > "$OFILE.edc"
    edje_cc "$OFILE.edc" "$OFILE.edj" 2>/dev/null
    rm "$OFILE.edc"
