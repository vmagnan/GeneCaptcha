#!/bin/bash

convert -density 300 $1 -depth 8 -strip -background white alpha off out.tiff
tesseract out.tiff tesseract 
cat tesseract.txt
feh $1
