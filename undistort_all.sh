#!/bin/bash

imagedir=./bordered/
fov=90 #this seems like a good FOV
for entry in "$imagedir"/*
do
  echo "$entry"
  name=$(basename "$entry" ".jpg")
  python3 undistort.py --i "$entry" --o ./undistorted/"$name".jpg --o_fov 90 --i_fov 110
done