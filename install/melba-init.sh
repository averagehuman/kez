#!/bin/bash

if [ -n "$1" ]; then
    root=$(dirname $1)
    dir=$(basename $1)
    envdir="$(cd $root && pwd)/$dir"
else
    envdir="$(pwd)/melba.env"
fi

if [ ! -e "$envdir" ]; then
    command -v conda >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        conda create --prefix "$envdir" --yes --mkdir numpy scipy ipython-notebook
    else
        command -v orb >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            orb init "$envdir"
        else
            command -v virtualenv >/dev/null 2>&1
            if [ $? -eq 0 ]; then
                virtualenv "$envdir"
            else
                echo "ERROR: couldn't create environment. Install either conda or virtualenv."
                exit 1
            fi
        fi
    fi
fi

pyexe="$envdir/bin/python"
pipexe="$envdir/bin/pip"

if [ ! -e "$pipexe" ]; then
    if [ ! -e "$pyexe" ]; then
        echo "ERROR: $pyexe not found - is $envdir a virtualenv?"
        exit 1
    else
        echo "installing pip into environment $envdir"
        getpip="https://raw.github.com/pypa/pip/master/contrib/get-pip.py"
        wget -O get-pip.py $getpip
        if [ ! -s get-pip.py ]; then
            echo "ERROR: invalid or non-existent file - get-pip.py"
            exit 1
        fi
        $pyexe get-pip.py
    fi
fi

    

