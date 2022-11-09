#!/bin/bash

imagedir=./214-1_small/
fov=90 #this seems like a good FOV
for entry in "$imagedir"/*
do
  echo "$entry"
  name=$(basename "$entry" ".jpg")
  python3 undistort.py --i "$entry" --o ./undistorted/"$name".jpg --o_fov 90
done