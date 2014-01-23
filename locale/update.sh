#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INDIR=$(pwd)

cd $DIR/../
# xgettext -d rmk.gabi -o locale/rmk.gabi.po *.py -j
# cd $INDIR

for FILE in $(find $DIR/*/LC_MESSAGES -type f -name "*.po")
do
	echo '' > messages.po # xgettext needs that file, and we need it empty
	find . -type f -iname "*.py" | xgettext -j -f -
	msgmerge -N $FILE messages.po > new.po
	mv new.po $FILE
	rm messages.po
done

cd $INDIR