# Standalone App for Participants

This folder contains code for a standalone executable (binary for Windows, Mac, and Linux) that can be distributed to participants to run the parsing of their sensitive data locally and generate a non-sensitive summary report that the participants can then submit to us.



## General commands to generate the executables:

The general principle to generate the exectutables is:

`pyinstaller --onefile --noconsole  --icon "logo.icns" --add-data="logo_small.gif:." --add-data="news_list.csv:." --exclude-module matplotlib --exclude-module zmq --exclude-module pandas --exclude-module numpy  --exclude-module PIL  --exclude-module urllib3 --exclude-module IPython --exclude-module sqlite3 --exclude-module pydoc --exclude-module shelve  mijnvoetsporen.py`

In case you have both the legacy Python2 pyinstaller binary and the Python3 pyinstaller binary installed, you can force your system to use the Python3 version like this:

`python3 -m PyInstaller --onefile --noconsole  --icon "logo.icns" --add-data="logo_small.gif:." --add-data="news_list.csv:." --exclude-module matplotlib --exclude-module zmq --exclude-module pandas --exclude-module numpy  --exclude-module PIL  --exclude-module urllib3 --exclude-module IPython --exclude-module sqlite3 --exclude-module pydoc --exclude-module shelve  mijnvoetsporen.py`

On Windows, you need to separate source and destination of data files with a `;` instead of a `:` and use a different icon, like this:

`pyinstaller --onefile --noconsole --icon "logo.ico" --add-data="logo_small.gif;." --add-data="news_list.csv;." --exclude-module matplotlib --exclude-module zmq --exclude-module pandas --exclude-module numpy  --exclude-module PIL  --exclude-module urllib3 --exclude-module IPython --exclude-module sqlite3 --exclude-module pydoc --exclude-module shelve  mijnvoetsporen.py`
`pyinstaller --onefile --noconsole --icon "logo.ico" --add-data="logo_small.gif;." --add-data="news_list.csv;." mijnvoetsporen.py`


## Shortcuts for generating the executables

### Linux

On Linux, you can simply run
`./build-linux.sh`. This will also autmatically solve the problem that you may run into a recursion error (see https://stackoverflow.com/a/51254042/3677739).
