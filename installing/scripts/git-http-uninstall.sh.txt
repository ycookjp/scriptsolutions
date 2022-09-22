#!/bin/bash
################################################################################
# Name    : git-http-uninstall.sh
# Usage   : git-http-uninstall.sh
################################################################################

# parse option
while getopts h OPT
do
  case $OPT in
    h|*)
        echo "Uninstall git, git-lfs, git-lfs-fcgi pakages."
        echo "Usage: `basename $0`"
        exit
        ;;
  esac
done
shift $(($OPTIND - 1))

# Determines package command.
__OS=`uname -r | sed -e 's/^[-0-9\.]*//g' -e 's/\.[a-z0-9_]*$//g'`
if [ ${__OS} = el7 ]; then \
  __PKGCMD=yum
else \
  __PKGCMD=dnf
fi

read -p "Uninstalling git-lfs-fcgi package. Hit any key to continue." -n 1; echo

# disable services
echo Disabling httpd and git-lfs-fcgi services ...
systemctl stop httpd git-lfs-fcgi
systemctl disable httpd git-lfs-fcgi

# remove Git LFS repository directory
echo Removing Git LFS repository /var/lib/git-lfs-fcgi/example.git ...
rm -rf /var/lib/git-lfs-fcgi/repository/example.git

# remove my-git-lfs-fcgi SELinxu package
echo Removing my-git-lfs-fcgi SELinux package ...
semodule -r my-git-lfs-fcgi

# remove example Git repository
rm -rf /var/lib/git/example.git
if [ `ls /var/lib/git/ | wc -l` -eq 0 ]; then
  rm -rf /var/lib/git
fi
rm -f /etc/httpd/conf.d/git-smart-http.conf

# remove my-antivirus-sudo SELinux package
echo Removing my-http-git SELinux package ...
semodule -r my-http-git

# remove git and git-lfs packages.
${__PKGCMD} remove -y git git-lfs

# remove git-lfs-fcgi package
${__PKGCMD} remove -y git-lfs-fcgi
