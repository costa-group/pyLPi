#!/bin/bash

UN=""
UP=""
FORCE=false
pvers="false"

for i in "$@"; do
    case $i in
	-up|--update)
	    UP="--upgrade"
	    UN=""
	    shift # past argument=value
	    ;;
	-un|--uninstall)
	    UP=""
	    UN="un"
	    shift # past argument=value
	    ;;
	-p=*|--python=*)
	    pvers="${i#*=}"
	    if [ "$pvers" = "2" ]; then
		P2=true
		P3=false
	    fi
	    if [ "$pvers" = "3" ]; then
		P3=true
		P2=false
	    fi
	    shift # past argument=value
	    ;;
	-f|--force)
	    FORCE=true
	    shift # past argument=value
	    ;;
	*)
	    >&2 cat  <<EOF 
ERROR: install.sh [OPTIONS]

[OPTIONS]

    -f | --force ) 
                   force default values: 
                   Install python dependencies and
                   Install UNIX packages

    -up | --update ) 
                   Update or Upgrade all the packages.

    -un | --uninstall )
                   Uninstall all except UNIX packages.

    -p=[VERSION] | --python=[VERSION] )
                   Install only for python version number [VERSION].
                   It has to be 2 or 3.

EOF
	    exit -1
	    ;;
    esac
done


exists(){
    command -v "$1" >/dev/null 2>&1
}


if [ "$pvers" = "false" ]; then
    if exists python2; then
	P2=true
    else
	P2=false
    fi
    
    if exists python3; then
	P3=true
    else
	P3=false
    fi
fi

flags=""

# check sudo permission
if [ "$EUID" -ne 0 ]; then
    flags=$flags" --user"
fi



# get base folder
if [ "$(uname -s)" = 'Linux' ]; then
    basedir=$(dirname "$(readlink -f "$0" )")
else
    basedir=$(dirname "$(readlink "$0" )")
fi

# Python 2 or 3 or both?
while [ "$P2" = "true" -a "$P3" = "true" ]; do
    read -p "Which python version do you want to use? [2/3/B] (default: B - Both)" yn
    case $yn in
        [2]*)
	    P3=false
	    break;;
	[3]* )
	    P2=false
	    break;;
        ""|[bB])
	    break;;
        * ) echo "Invalid option."; echo $yn;;
    esac
done


if [ "$FORCE" = "true" ]; then
    pdepen=true
    udepen=true
else

    pdepen=true

    while true; do
	read -p "Do you want to install the standar Python dependencies? [Y/n]" yn
	case $yn in
            [yY][eE][sS]|[yY])
		break;;
	    [nN][oO]|[nN])
		echo "Be sure to have them already installed, otherwise the installation will crash."
		pdepen=false
		break;;
            "")
		break;;
            * ) echo "Invalid option."; echo $yn;;
	esac
    done
    
    udepen=$pdepen
    while [[ $pdepen == true ]]; do
	read -p "Do you want to install the UNIX dependencies? [Y/n]" yn
	case $yn in
            [yY][eE][sS]|[yY])
		break;;
	    [nN][oO]|[nN])
		echo "Be sure to have them already installed, otherwise the installation will crash."
		udepen=false
		break;;
            "")
		break;;
            * ) echo "Invalid option."; echo $yn;;
	esac
    done
fi


if [ "$udepend" = "true" ]; then
    sudo apt-get install libppl_dev cython build_essentials python_sphinx libmpfr_dev libmpc_dev libgmp_dev
fi


install()
{
    if [ "$UN" = "un" ]; then
	flags=" -y"
    else
	flags=$flags" $UP"
    fi
    vers=$1
    echo "----------------------------------"
    echo "Installing pyLPi on Python $vers"
    echo "----------------------------------"
    if [ "$pdepen" = "true" ]; then
	pip$vers $UN"install" $flags z3 cython cysignals virtualenv

	if [ "$vers" = "2" ]; then
	    pip2 $UN"install" $flags gmpy2
	    pip2 $UN"install" $flags pplpy
	else
	    pip3 $UN"install" $flags git+https://github.com/aleaxit/gmpy.git#egg=gmpy2
	    pip3 $UN"install" $flags git+https://github.com/videlec/pplpy.git#egg=pplpy
	fi	
    fi

    #pip$vers $UN"install" $flags git+https://github.com/jesusjda/pyLPi.git#egg=pyLPi
    python$vers $basedir/setup.py build --build-base=$basedir
    python$vers $basedir/setup.py install 


}

if [ "$P2" = "true" ]; then
    easy_install $flags pip
    install 2
fi

if [ "$P3" = "true" ]; then
    if [ "$udepend" = "true" ]; then
	sudo apt-get install cython3
    fi
    easy_install3 $flags pip
    install 3
fi


echo "Success!"
