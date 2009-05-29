#!/bin/bash

# wraper to register fonts so that preview uses them.

python \
~/dabo-trunk/ide/RD.py \
-r /usr/share/fonts/type1/gsfonts/n019003l.afm \
-r /usr/share/fonts/type1/gsfonts/n019004l.afm  \
-r /usr/share/fonts/truetype/freefont/FreeSans.ttf \
badge.rfxml 
