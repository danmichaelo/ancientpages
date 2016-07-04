#!/bin/sh

echo "=== This is DanmicholoBot running on $(hostname) ==="
date
. ENV/bin/activate
python run.py

