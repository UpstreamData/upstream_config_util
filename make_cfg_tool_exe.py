"""
Make a build of the config tool.

Usage: make_config_tool.py build

The build will show up in the build directory.
"""
import datetime
import sys
import os
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

version = datetime.datetime.now()
version = version.strftime("%y.%m.%d")
PACKAGES = [
    "aiohttp",
    "aiosignal",
    "anyio",
    "async_timeout",
    "asyncssh",
    "attrs",
    "certifi",
    "cffi",
    "charset_normalizer",
    "contourpy",
    "cryptography",
    "cssselect2",
    "cycler",
    "exceptiongroup",
    "frozenlist",
    "h11",
    "httpcore",
    "httpx",
    "idna",
    "kiwisolver",
    "lxml",
    "matplotlib",
    "multidict",
    "numpy",
    "packaging",
    "passlib",
    "PIL",
    "pyaml",
    "pyasic",
    "pycparser",
    "pyparsing",
    "pyperclip",
    "PySimpleGUI",
    "pyaml",
    "reportlab",
    "setuptools_scm",
    "six",
    "sniffio",
    "svglib",
    "tinycss2",
    "toml",
    "tomli",
    "typing_extensions",
    "webencodings",
    "yarl",
]


setup(
    name="UpstreamCFGUtil.exe",
    version=version,
    description="Upstream Data Config Utility Build",
    options={
        "build_exe": {
            "build_exe": f"{os.getcwd()}\\build\\UpstreamCFGUtil-{version}-{sys.platform}\\",
            "include_files": [
                os.path.join(os.getcwd(), "settings/settings.toml"),
                os.path.join(os.getcwd(), "README.md"),
            ],
            "packages": PACKAGES,
        },
    },
    executables=[
        Executable(
            "main.py",
            base=base,
            icon="icon.ico",
            target_name="UpstreamCFGUtil.exe",
        )
    ],
)
