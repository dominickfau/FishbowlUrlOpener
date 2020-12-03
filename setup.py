import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
# build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).

target = Executable(
    script="FishbowlUrlOpener.py",
    base="Win32GUI",
    icon="appIcon.ico"
    )

setup(
    name="Fishbowl_URL_Opener",
    version="1.0.0",
    description="Connects to a fishbowl database, then allows user to enter a part number to lookup.",
    author="Dominick Faurote",
    # options={"build_exe": options},
    executables=[target]
    )