#!/bin/bash

module load python/2.7
module load chqpoint/0.1
module load texlive

root=..
$root/makereport.py --analysisroot $root/data --chqpointmap $root/data/chqpoint.json --htmltemplate report.html --htmldestfile out.html --pdftemplate report.tex --pdfdestfile out.pdf --debug

