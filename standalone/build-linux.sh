#!/bin/sh

echo Clean up...

rm -rf build
rm -rf dist/
rm -rf __pycache__/

echo Trying to build...


if pyinstaller --onefile --noconsole  --icon "logo.icns" --add-data="logo_small.gif:." --add-data="news_list.csv:." --exclude-module matplotlib --exclude-module zmq --exclude-module pandas --exclude-module numpy  --exclude-module PIL  --exclude-module urllib3 --exclude-module IPython --exclude-module sqlite3 --exclude-module pydoc --exclude-module shelve  mijnvoetsporen.py  ; then
    echo Done!
else
    echo This did not work, but at least we have a spec file now.
    echo Increasing the recursion limit in spec file
    sed -i '2iimport sys\nsys.setrecursionlimit(5000)' mijnvoetsporen.spec 
    echo Rebuilding based on modified spec file...
    pyinstaller --onefile --noconsole  --icon "logo.icns" --add-data="logo_small.gif:." --add-data="news_list.csv:." --exclude-module matplotlib --exclude-module zmq --exclude-module pandas --exclude-module numpy  --exclude-module PIL  --exclude-module urllib3 --exclude-module IPython --exclude-module sqlite3 --exclude-module pydoc --exclude-module shelve  mijnvoetsporen.py
fi
