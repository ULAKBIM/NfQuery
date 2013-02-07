#!/bin/sh

NAME=NfQuery


if test $# -ne 2; then
    echo "usage: $0 type{plugin|queryserver} version"
else
    TYPE=$1
    VERSION=$2
    FULLNAME=${NAME}-${TYPE}-v${VERSION}
    echo ${FULLNAME}

    echo "Cleaning backup files."
    find . -name "*~" | xargs rm
    cp -r ./plugin ${FULLNAME}
    tar czf ${FULLNAME}.tar.gz ${FULLNAME}
fi 

