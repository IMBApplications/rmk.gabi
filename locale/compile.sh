#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for FILE in $(find $DIR/LC_MESSAGES -type f -name "*.po")
do
	dirname=$(dirname $FILE)
	basename=$(basename $FILE)
	filename="${basename%.*}"

	echo "Compiling $FILE"
	msgfmt -cv -o $dirname/$filename.mo $FILE
done
