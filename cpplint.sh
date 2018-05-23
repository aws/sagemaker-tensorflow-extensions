find . -name \*.hpp -or -name \*.cpp \
	| xargs cpplint --linelength=120 --filter=-build/c++11 2>&1 \
	| grep -v "Done processing "
