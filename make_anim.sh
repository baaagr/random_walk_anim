#!/bin/bash

ffmpeg -framerate 20 -i frames/f_%05d.png -c:v libx264 anim.mp4
