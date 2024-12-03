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
    "aiofiles", "annotated-types", "anyio", "asyncssh", "betterproto", "certifi", "cffi", "chardet", "contourpy",
    "cryptography", "cssselect2", "cycler", "exceptiongroup", "fonttools", "freesimplegui", "grpclib", "h11", "h2",
    "hpack", "httpcore", "httpx", "hyperframe", "idna", "importlib-resources", "kiwisolver", "lxml", "matplotlib",
    "multidict", "numpy", "packaging", "passlib", "pillow", "pyaml", "pyasic", "pycparser", "pydantic-core", "pydantic",
    "pyparsing", "pyperclip", "python-dateutil", "pyyaml", "reportlab", "six", "sniffio", "svglib", "tinycss2",
    "tomli-w", "tomli", "typing-extensions", "webencodings", "zipp"]


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
