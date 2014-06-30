#!/bin/bash

VERSION='2.0.3'
if [[ -n $1 ]]; then
    VERSION="$1"
fi

JURL="http://code.jquery.com/jquery-${VERSION}.js"
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OLDDIR="$THIS_DIR"

cd "$THIS_DIR"
mkdir -p static/js
cd static/js

curl -L "$JURL" > "jquery-${VERSION}.js"

cd -
