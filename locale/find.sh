#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for FILE in $DIR/../*.py
do
	basename=$(basename $FILE)
	filename="${basename%.*}"

	echo "Searching in $basename"
	xgettext -d rmk.gabi -o $DIR/$filename.po $FILE
done