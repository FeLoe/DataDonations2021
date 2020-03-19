# Standalone App for Participants

This folder contains code for a standalone executable (binary for Windows, Mac, and Linux) that can be distributed to participants to run the parsing of their sensitive data locally and generate a non-sensitive summary report that the participants can then submit to us.


Command to generate the executables:
`pyinstaller --onefile --noconsole mijnvoetsporen.py` or `python3 -m PyInstaller --onefile --noconsole mijnvoetsporen.py`