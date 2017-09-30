#!/usr/bin/env bash
pyinstaller --windowed \
	--distpath build \
	--workpath build/tmp \
	--icon=D.ico \
	--add-data D.ico:. --add-data D.png:. --add-data themes:themes --add-data translations:translations \
	-F durak.pyw
