#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INDIR=$(pwd)

cd $DIR/../
xgettext -d rmk.gabi -o locale/rmk.gabi.po *.py
cd $INDIR
