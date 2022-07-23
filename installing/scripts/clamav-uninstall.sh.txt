#!/bin/sh
################################################################################
# Name    : clamav-uninstall.sh
# Usage   : clamav-uninstall.sh [<scheme>://<proxy-server> [proxy-port]]
################################################################################

# parse option
while getopts h OPT
do
  case $OPT in
    h|*)
        echo "Uninstall clamav, clamav-update, clamd packages."
        echo "Usage: `basename $0`"
        exit
        ;;
  esac
done
shift $(($OPTIND - 1))

__PROXY_SERVER=`echo $1 | sed -e 's/\//\\\\\//g'`
__PROXY_PORT=$2
__ISOLATED_DIR=/var/tmp/clamscan/isolated/

# Determines package command.
__OS=`uname -r | sed -e 's/^[-0-9\.]*//g' -e 's/\.[a-z0-9_]*$//g'`
if [ ${__OS} = el7 ]; then \
  __PKGCMD=yum
else \
  __PKGCMD=dnf
fi

read -p "Uninstalling clamav packages. Hit any key to continue." -n 1; echo

# stop clamav-freshclam and clamd@scan service
echo Stopping clamd@scan service ...
systemctl stop clamd@scan
echo Stopping clamav-freshclam service ...
systemctl stop clamav-freshclam

# remove symbolic linc
echo Removing /etc/clamd.conf symbolic link ...
rm -f /etc/clamd.conf

# remove my-antivirus-sudo SELinux package
echo Removing my-antivirus-sudo SELinux package ...
semodule -r my-antivirus-sudo

# remove my-antivirus-daemon SELinux package
echo Removing my-antivirus-daemon SELinux package ...
semodule -r my-antivirus-daemon

# SELinux boolean value
echo Setting SELinux boolean value ...
setsebool -P antivirus_can_scan_system 0

# remove isolated directory
echo Removing isolated directory ...
rm -rf /var/tmp/clamscan/isolated/

# remove scan.conf backup
echo Removing /etc/clamd.d/scan.conf.orig ...
rm -f /etc/clamd.d/scan.conf.orig

# remove freshclam.conf backup
echo Removing /etc/freshclam.conf.orig ...
rm -f /etc/freshclam.conf.orig

# remove clamav, clamav-update and clamd packages.
${__PKGCMD} remove -y clamav clamav-update clamd

# show message
echo Following files / directories are remained.
echo "  o /var/tmp/clamscan/isolated/"
echo "  o /var/log/freshclam.log"
echo "  o /var/log/clamd.scan"
echo "  o /var/log/clamonacc.log"
