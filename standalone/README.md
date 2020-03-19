# Standalone App for Participants

This folder contains code for a standalone executable (binary for Windows, Mac, and Linux) that can be distributed to participants to run the parsing of their sensitive data locally and generate a non-sensitive summary report that the participants can then submit to us.


Command to generate the executables:

`pyinstaller --onefile --noconsole --add-data="logo_small.gif:." mijnvoetsporen.py`

In case you have both the legacy Python2 pyinstaller binary and the Python3 pyinstaller binary installed, you can force your system to use the Python3 version like this:

`python3 -m PyInstaller --onefile --noconsole --add-data="logo_small.gif:." mijnvoetsporen.py`

On Windows, you need to separate source and destination of data files with a `;` instead of a `:`, like this:

`pyinstaller --onefile --noconsole --add-data="logo_small.gif;." mijnvoetsporen.py`
