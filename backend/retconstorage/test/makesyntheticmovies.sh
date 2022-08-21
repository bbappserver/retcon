#!/bin/bash
ffmpeg -i bigbuckclipped.mp4 -vf scale=320:240 bigbuckclippedshrink.mp4
ffmpeg -i bigbuckclipped.mp4 -ss 00:00:03 -t 00:00:08 -vf scale=320:240 bigbuckclippedshrinkcut.mp4

ffmpeg -i bigbuckclipped.mp4 -ss 00:00:03 -t 00:00:04 -vf scale=320:240 bigbuckclippedshrinkcut.gif

ffmpeg -ss 00:00:00 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen1.jpg
ffmpeg -ss 00:00:01 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen2.jpg
ffmpeg -ss 00:00:02 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen3.jpg
ffmpeg -ss 00:00:03 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen4.jpg
ffmpeg -ss 00:00:08 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen5.jpg
ffmpeg -ss 00:00:08 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen5.identical.jpg
ffmpeg -ss 00:00:08 -i bigbuckclipped.mp4 -vf scale=320:240 -vframes 1 -q:v 2 bigbuckscreen5.small.jpg
ffmpeg -ss 00:00:09 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen6.jpg
ffmpeg -ss 00:00:12 -i bigbuckclipped.mp4 -vframes 1 -q:v 2 bigbuckscreen7.jpg