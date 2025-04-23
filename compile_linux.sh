#!/bin/bash
nuitka --onefile --follow-imports --lto=yes --include-data-dir=./modules/static=modules/static --include-data-dir=./modules/templates=modules/templates --jobs=8 main.py