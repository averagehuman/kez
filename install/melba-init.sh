#!/bin/bash

###############################################################################
#
# Create a virtual environment suitable for building Pelican blogs from source
#
# Usage:
#
#    $ ./mkenv test.env
#
###############################################################################

# If a directory has been given as first parameter, set 'envdir' to its
# absolute path. Otherwise use a default directory within the current
# working directory
if [ -n "$1" ]; then
    root=$(dirname $1)
    dir=$(basename $1)
    envdir="$(cd $root && pwd)/$dir"
else
    echo "ERROR: an environment name must be given"
    exit 1
fi

# If the environment 'envdir' does not exist, create it. By default, use conda
# if it is available, falling back to virtualenv.
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

# Install `pip` if it does not exist
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


