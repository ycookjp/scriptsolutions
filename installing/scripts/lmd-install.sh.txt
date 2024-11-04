#!/bin/sh
################################################################################
# Name  : lmd-install.sh
# Usage : lmd-install.sh [--proxy-host={<name>|<ipaddr>} --proxy-port=<port-no>
#             --email-user=<user-name>]
################################################################################

# options
while [ $# -gt 0 ]; do
  case $1 in
  --*)
    __optName=${1%%=*}
    __optValue=${1#*=}
    # if options's value is not specified, value shuld be '1'
    if [ x$__optName == x$__optValue ]; then
      __optValue=1
    fi
    __optName=${__optName//-/_}
    echo "${__optName}=${__optValue}"
    eval "${__optName}=${__optValue}"
    shift
    ;;
  -h)
    echo "__help=1"
    __help=1
    shift
    ;;
  -*)
    shift
    ;;
  *)
    break
    ;;
  esac
done

if [ x$__help != x ]; then
  cat << __EOF
# Usage : lmd-install.sh [--proxy-host={<name>|<ipaddr>} --proxy-port=<port-no>
#             --email-user=<user-name>]
__EOF
  exit
fi

if [ x$__proxy_host != x ]; then
  __curlxopt="-x $__proxy_host"
  if [ x$__proxy_port != x ]; then
      __curlxopt=${__curlxopt}:${__proxy_port}
  fi
fi

__tmpdir=/tmp/lmd-install-$$
__source_url=https://www.rfxn.com/downloads/maldetect-current.tar.gz
__tmplmddir=${__tmpdir}/$(basename $__source_url | sed 's/\..*$//g')
__tmpsedir=${__tmpdir}/selinux

# Download linux malware detect source archive.
echo Downloading $__source_url ...
mkdir -p $__tmplmddir $__tmpsedir
(
  cd $__tmplmddir
  curl $__curlxopt -LO $__source_url
)

# Install Linux Mulware Detect
echo Installing Linux Malware Detect ...
rm -rf /usr/local/maldetect
tar xvfzC ${__tmplmddir}/$(basename $__source_url) $__tmplmddir
(
  cd ${__tmplmddir}/maldetect-*/
  ./install.sh
)

# Set fs.inotify.max_user_watches
echo Setting /etc/sysctl.conf
sed '/^[ \t]*fs.inotify.max_user_watches/d' -i /etc/sysctl.conf
echo fs.inotify.max_user_watches = 524288 >> /etc/sysctl.conf

# Install required packages
if [ $(dnf list --installed -q ed inotify-tools perl cronie | wc -l) -lt 4 ]; then
  echo Installing related packages ...
  dnf install -y ed inotify-tools perl cronie
fi

# Install SELinux policy
if [ $(dnf list --installed -q selinux-policy | wc -l) -gt 0 ]; then
  echo Setting SELinux configurations ...
  dnf install -y checkpolicy
  cat << __EOF >> $__tmpsedir/my-init_unlink.te
module my-init_unlink 1.0;
require {
  attribute init_t;
  attribute usr_t;
  class file unlink;
}
#============= init_t ==============
allow init_t usr_t:file unlink;
__EOF
  checkmodule -m -o $__tmpsedir/my-init_unlink.mod $__tmpsedir/my-init_unlink.te
  semodule_package -o $__tmpsedir/my-init_unlink.pp -m $__tmpsedir/my-init_unlink.mod
  semodule -i $__tmpsedir/my-init_unlink.pp
fi

# Configure /usr/local/maldetect/ignore_inotify
echo Setting /usr/local/maldetect/ignore_inotify ...
cat << __EOF >> /usr/local/maldetect/ignore_inotify
^/tmp/[0-9]*_[0-9]*-scantemp\.[0-9a-z]*
^/dev/.*
^/proc/.*
^/var/log/.*
^/var/lib/clamav/.*
^/var/spool/quarantine/.*
__EOF

# Configure /usr/local/maldetect/monitor_paths
echo Setting /usr/local/maldetect/monitor_paths ..,
cat << __EOF >> /usr/local/maldetect/monitor_paths
/afs
/boot
/etc
/home
/media
/mnt
/opt
/root
/run
/srv
/tmp
/usr
/var
__EOF

# Configure /usr/lib/systemd/system/maldet.service
echo Setting /usr/lib/systemd/system/maldet.service ...
sed 's/\(^ExecStart=\/usr\/local\/maldetect\/maldet --monitor \).*$/\1\/usr\/local\/maldetect\/monitor_paths/g' \
    -i /usr/lib/systemd/system/maldet.service

# Configure /usr/local/maldetect/maldet
echo Setting /usr/local/maldetect/maldet ...
sed 's/\(^[ \t]*\)\(genalert digest\)/\1LANG=C \2/g' \
    -i /usr/local/maldetect/maldet

# Configure /usr/local/maldetect/conf.maldet
echo Setting /usr/local/maldetect/conf.maldet ...
sed 's/\(^[ \t]*scan_ignore_root=\).*$/\1"0"/g' -i /usr/local/maldetect/conf.maldet
if [ x$__proxy_host != x ]; then
  sed '/^[ \t]*web_proxy=.*$/d' -i /usr/local/maldetect/conf.maldet
  echo web_proxy=${__proxy_host}:${__proxy_port} >> /usr/local/maldetect/conf.maldet
fi

# Configre /usr/lib/systemd/system/maldet.service
if [ -f /usr/lib/systemd/system/clamd@.service ]; then
  echo Setting /usr/lib/systemd/system/maldet.service ...
  sed 's/\(^After=.*\)/\1 clamd@scan.service/g' \
      -i /usr/lib/systemd/system/maldet.service
fi

# Configure Email alert settings
if [ x$__email_user != x ]; then
  if [ $(dnf list --installed -q s-nail sendmail | wc -l) -lt 2 ]; then
    echo Installing packages related to mail alert ...
    dnf install -y s-nail sendmail
    systemctl enable sendmail
  fi
  echo Setting /usr/local/maldetect/conf.maldet ...
  sed -e 's/\(^[ \t]*email_alert=\).*$/\1"1"/g' \
      -e "s/\([ \t]*email_addr=\).*$/\1\"$__email_user\"/g" \
      -i /usr/local/maldetect/conf.maldet
fi

echo "Linux Malware Detect installed."
# Remove temporary directory
echo Removing $__tmpdir ...
rm -rf $__tmpdir
