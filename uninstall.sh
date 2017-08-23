#!/bin/bash

# check sudo permission
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


# get base folder
if [ "$(uname -s)" = 'Linux' ]; then
    basedir=$(dirname "$(readlink -f "$0" )")
else
    basedir=$(dirname "$(readlink "$0" )")
fi


# select where to uninstall
P2=true
P3=true
while true; do
    read -p "Which python version do you want to use? [2/3/B] (default: B - Both) " yn
    case $yn in
        [2]*)
	    P3=false
	    break;;
	[3]* )
	    P2=false
	    break;;
        "")
	    break;;
        * )
	    echo "Invalid option.";;
    esac
done

if [ "$P2" = true ]; then
    echo "Uninstalling... (python 2)"
    python2 $basedir/setup.py install --record $basedir/files2.txt > /dev/null
    cat $basedir/files2.txt | xargs -I {} rm -rf
    rm -rf $basedir/files2.txt
    echo "done!"
fi

if [ "$P3" = true ]; then
    echo "Uninstalling... (python 3)"
    python3 $basedir/setup.py install --record $basedir/files3.txt > /dev/null
    cat $basedir/files3.txt | xargs -I {} rm -rf
    #rm -rf $basedir/files3.txt
    echo "done!"
fi


