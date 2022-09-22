#!/bin/sh
################################################################################
# Name    : clamav-install.sh
# Usage   : clamav-install.sh [proxy-server [proxy-port]]
################################################################################

# parse option
while getopts h OPT
do
  case $OPT in
    h|*)
        echo "Usage: `basename $0` [proxy-server [proxy-port]]"
        exit
        ;;
  esac
done
shift $(($OPTIND - 1))

__PROXY_SERVER=`echo $1 | sed -e 's/\//\\\\\//g'`
__PROXY_PORT=$2
__ISOLATED_DIR=/var/tmp/clamscan/isolated

# Determines package command.
__OS=`uname -r | sed -e 's/^[-0-9\.]*//g' -e 's/\.[a-z0-9_]*$//g'`
if [ ${__OS} = el7 -o  ${__OS} = el6 ]; then \
  __PKGCMD=yum
else \
  __PKGCMD=dnf
fi

read -p "Installing clamav packages. Hit any key to continue." -n 1; echo

# install neccesary packages
${__PKGCMD} install -y sed checkpolicy policycoreutils
if [ ${__PKGCMD} = yum ]; then
  ${__PKGCMD} install -y policycoreutils-python
fi

# install clamav, clamav-update and clamd packages.
${__PKGCMD} install -y clamav clamav-update clamd

################################################################################
# freshclam service configuration
################################################################################
# configure /etc/freshclam.conf
echo Configuring /etc/freshclam.conf ...

if [ ! -e /etc/freshclam.conf.orig ]; then \
  cp -dpf /etc/freshclam.conf /etc/freshclam.conf.orig
fi

sed -i /etc/freshclam.conf \
    -e 's/^#UpdateLogFile /UpdateLogFile /g' \
    -e 's/^#NotifyClamd .*$/NotifyClamd \/etc\/clamd.d\/scan.conf/g'
if [ x${__PROXY_SERVER} != x ]; then \
  sed -i /etc/freshclam.conf -e "s/^#HTTPProxyServer .*$/HTTPProxyServer http:\/\/${__PROXY_SERVER}\nHTTPProxyServer https:\/\/${__PROXY_SERVER}/g"
fi
if [ x${__PROXY_PORT} != x ]; then \
  sed -i /etc/freshclam.conf -e "s/^#HTTPProxyPort .*$/HTTPProxyPort ${__PROXY_PORT}/g"
fi 

# create log file
echo Creating /var/log/freshclam.log ...

touch /var/log/freshclam.log
chmod 600 /var/log/freshclam.log
chown clamupdate:clamupdate /var/log/freshclam.log

################################################################################
# clamonacc service configuration
################################################################################
# configure clamonacc.service
if [ -f /usr/lib/systemd/system/clamav-clamonacc.service ]; then
  echo Configuring /usr/lib/systemd/system/clamav-clamonacc.service ...
  sed -i /usr/lib/systemd/system/clamav-clamonacc.service \
      -e 's/\(^ExecStart *=.*\/clamonacc .*$\)/\1 --log=\/var\/log\/clamonacc.log --fdpass\nCPUQuota=50%/g'
fi

################################################################################
# clamd service configuration
################################################################################
# configure clamd@.service
if [ -f /usr/lib/systemd/system/clamd@.service ]; then
  echo Configuring /uar/lib/systemd/system/clamd@.service ...
  sed -i /usr/lib/systemd/system/clamd@.service \
      -e 's/\(^ExecStart *=.*\/clamd .*$\)/\1\nMemoryLimit=512M/g' \
      -e 's/\(^TimeoutStartSec *=.*$\)/#\1\nTimeoutStartSec=600/g'
fi

# generate scan.conf
echo Creating /etc/clamd.d/scan.conf ...

if [ ! -e /etc/clamd.d/scan.conf.orig ]; then \
  cp -dpf /etc/clamd.d/scan.conf /etc/clamd.d/scan.conf.orig
fi

cat << __EOF > /etc/clamd.d/scan.conf
################################################################################
# Settings for clamd daemon and font ends.
################################################################################
LogFile /var/log/clamd.scan
LogTime yes
LogSyslog yes
ExtendedDetectionInfo yes

# LocalSocket connection
LocalSocket /run/clamd.scan/clamd.sock
LocalSocketGroup virusgroup
LocalSocketMode 660
# TCPSocket connection
#TCPSocket 3310
#TCPAddr 127.0.0.1

User clamscan
ExitOnOOM yes

# Setting for hight performance
# MaxThreads*MaxRecursion + (MaxQueue - MaxThreads) + 6< RLIMIT_NOFILE (usual
# max is 1024).
MaxQueue 200
MaxThreads 20

MaxDirectoryRecursion 30

################################################################################
# ExcludePath definitions.
################################################################################
# exclude isolated dir
ExcludePath ^${__ISOLATED_DIR}/

# exclude /dev, /proc and /sys
ExcludePath ^/dev/
ExcludePath ^/proc/
ExcludePath ^/sys/

# avoid 'Not supported file type'
ExcludePath ^/run/
#ExcludePath ^/tmp/
ExcludePath ^/var/lib/gssproxy/
ExcludePath ^/var/lib/nfs/
ExcludePath ^/var/lib/sss/

# avoid 'lstat() faild'
ExcludePath ^/etc/.*shadow.*
ExcludePath ^/etc/audit/
ExcludePath ^/etc/security/
ExcludePath ^/etc/selinux/
ExcludePath ^/var/lib/selinux/
ExcludePath ^/var/log/audit/

# exclude clamav related file/dir
ExcludePath ^/etc/clamd\.d/
ExcludePath ^/etc/freshclam\.conf
ExcludePath ^/etc/logrotate\.d/clamav-update
ExcludePath ^/run/clamd\.scan/
ExcludePath ^/usr/bin/clambc
ExcludePath ^/usr/bin/clamconf
ExcludePath ^/usr/bin/clamdscan
ExcludePath ^/usr/bin/clamdtop
ExcludePath ^/usr/bin/clamscan
ExcludePath ^/usr/bin/clamsubmit
ExcludePath ^/usr/bin/freshclam
ExcludePath ^/usr/bin/sigtool
ExcludePath ^/usr/lib/systemd/system/clamav-clamonacc\.service
ExcludePath ^/usr/lib/systemd/system/clamav-freshclam\.service
ExcludePath ^/usr/lib/systemd/system/clamd@\.service
ExcludePath ^/usr/lib/systemd/system/clamonacc\.service
ExcludePath ^/usr/lib/tmpfiles\.d/clamd\.scan\.conf
ExcludePath ^/usr/lib64/libclamav\.so\.9.*
ExcludePath ^/usr/lib64/libclammspack\.so\.0.*
ExcludePath ^/usr/lib64/libfreshclam\.so\.2.*
ExcludePath ^/usr/sbin/clamd
ExcludePath ^/sbin/clamd
ExcludePath ^/usr/sbin/clamonacc
ExcludePath ^/sbin/clamonacc
ExcludePath ^/var/lib/clamav/
ExcludePath ^/var/log/clamd\.scan
ExcludePath ^/var/log/clamdscan\.log
ExcludePath ^/var/log/clamonacc\.log
ExcludePath ^/var/log/freshclam\.log
ExcludePath ^/var/spool/quarantine/

# exclude SE-Linux files
ExcludePath ^/etc/dbus-1/system.d/org\.selinux\.conf
ExcludePath ^/etc/pam.d/polkit-1
ExcludePath ^/etc/polkit-1
ExcludePath ^/etc/selinux
ExcludePath ^/etc/sestatus\.conf
ExcludePath ^/etc/sysconfig/selinux
ExcludePath ^/usr/bin/audit2allow
ExcludePath ^/usr/bin/audit2why
ExcludePath ^/usr/bin/chcat
ExcludePath ^/usr/bin/pkaction
ExcludePath ^/usr/bin/pkcheck
ExcludePath ^/usr/bin/pkexec
ExcludePath ^/usr/bin/pkla-admin-identities
ExcludePath ^/usr/bin/pkla-check-authorization
ExcludePath ^/usr/bin/pkttyagent
ExcludePath ^/usr/bin/secon
ExcludePath ^/usr/bin/semodule_expand
ExcludePath ^/usr/bin/semodule_link
ExcludePath ^/usr/bin/semodule_package
ExcludePath ^/usr/bin/semodule_unpackage
ExcludePath ^/usr/bin/sestatus
ExcludePath ^/usr/lib/polkit-1
ExcludePath ^/usr/lib/rpm/macros.d/macros\.selinux-policy
ExcludePath ^/usr/lib/systemd/system-generators/selinux-autorelabel-generator\.sh
ExcludePath ^/usr/lib/systemd/system/polkit\.service
ExcludePath ^/usr/lib/systemd/system/selinux-autorelabel-mark\.service
ExcludePath ^/usr/lib/systemd/system/selinux-autorelabel\.service
ExcludePath ^/usr/lib/systemd/system/selinux-autorelabel\.target
ExcludePath ^/usr/lib/systemd/system/selinux-check-proper-disable\.service
ExcludePath ^/usr/lib/tmpfiles.d/selinux-policy\.conf
ExcludePath ^/usr/lib64/girepository-1\.0/Polkit-1\.0\.typelib
ExcludePath ^/usr/lib64/girepository-1\.0/PolkitAgent-1\.0\.typelib
ExcludePath ^/usr/lib64/libpolkit-agent-1\.so.*
ExcludePath ^/usr/lib64/libpolkit-gobject-1.so.*
ExcludePath ^/usr/lib64/libpolkit-qt5-agent-1.so.*
ExcludePath ^/usr/lib64/libpolkit-qt5-core-1.so.*
ExcludePath ^/usr/lib64/libpolkit-qt5-gui-1.so.*
ExcludePath ^/usr/libexec/selinux/
ExcludePath ^/usr/sbin/fixfiles
ExcludePath ^/usr/sbin/genhomedircon
ExcludePath ^/usr/sbin/load_policy
ExcludePath ^/usr/sbin/restorecon
ExcludePath ^/usr/sbin/restorecon_xattr
ExcludePath ^/usr/sbin/semanage
ExcludePath ^/usr/sbin/semodule
ExcludePath ^/usr/sbin/sestatus
ExcludePath ^/usr/sbin/setfiles
ExcludePath ^/usr/sbin/setsebool
ExcludePath ^/var/lib/polkit-1/
ExcludePath ^/var/lib/selinux/targeted/

# exclude lock files
ExcludePath ^/var/lock/
ExcludePath ^/var/log/journal/
ExcludePath ^/var/run/

# exclude dhf cache
ExcludePath ^/var/cache/dnf/

# exclude media directory
#ExcludePath ^/media/

# exclude log directory
ExcludePath ^/var/log/

################################################################################
# Virus Event definition
################################################################################
#MaxDirectoryRecursion 20
VirusEvent for loggedin in \`ps -e -o user h | sort | uniq\`; do if [ \`cat /etc/shadow | grep -e "^\${loggedin}:[^\*^\!]" | wc -l\` -gt 0 ]; then for dispno in \`find /tmp -type f -name '.X*-lock' | sed -e 's/.*\.X//g' -e 's/-lock\$//g'\`; do sudo -u \$loggedin DISPLAY=:\$dispno DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/\$(id -u \$loggedin)/bus notify-send 'VIRUS ALERT' "Virus found at \${CLAM_VIRUSEVENT_FILENAME}"; done; fi; done

################################################################################
# Settings for On-Access Scanning
################################################################################
#OnAccessMaxFileSize 500M
OnAccessMaxThreads 10

#-------------------------------------------------------------------------------
# OnAccessIncludePath
#-------------------------------------------------------------------------------
# Do not include config, library and following directories.
# /dev
# /etc
# /proc
# /run
# /sys
# /tmp
# /usr/lib
# /usr/lib64
# /var/cache/dnf

# Resitrict include path to user datas
OnAccessIncludePath /home
#OnAccessIncludePath /lost+found
OnAccessIncludePath /media
OnAccessIncludePath /mnt
OnAccessIncludePath /opt
OnAccessIncludePath /root
OnAccessIncludePath /run/media
#OnAccessIncludePath /srv
#OnAccessIncludePath /tmp
#OnAccessIncludePath /usr/bin
OnAccessIncludePath /usr/games
#OnAccessIncludePath /usr/include
#OnAccessIncludePath /usr/libexec
OnAccessIncludePath /usr/local
#OnAccessIncludePath /usr/sbin
OnAccessIncludePath /usr/share
OnAccessIncludePath /usr/src

# Include indivisual /var sub dirs.
# Following directories shuld be excluded.
# - lib
# - log
# - lock (symbolic link)
# - mail (symbolic link)
# - run (symbolic link)
#OnAccessIncludePath /var/account
#OnAccessIncludePath /var/adm
OnAccessIncludePath /var/cache
#OnAccessIncludePath /var/crash
#OnAccessIncludePath /var/db
#OnAccessIncludePath /var/empty
OnAccessIncludePath /var/ftp
OnAccessIncludePath /var/games
#OnAccessIncludePath /var/kerberos
OnAccessIncludePath /var/local
#OnAccessIncludePath /var/log
OnAccessIncludePath /var/nfs
OnAccessIncludePath /var/opt
#OnAccessIncludePath /var/preserve
#OnAccessIncludePath /var/spool
OnAccessIncludePath /var/tmp
#OnAccessIncludePath /var/yp

#-------------------------------------------------------------------------------
# OnAccessExcludePath
#-------------------------------------------------------------------------------
# exclude clamav related file/dir
OnAccessExcludePath /etc/clamd.d
OnAccessExcludePath /etc/clamd.d/scan.conf
OnAccessExcludePath /etc/freshclam.conf
OnAccessExcludePath /usr/bin/clambc
OnAccessExcludePath /usr/bin/clamconf
OnAccessExcludePath /usr/bin/clamdscan
OnAccessExcludePath /usr/bin/clamdtop
OnAccessExcludePath /usr/bin/clamscan
OnAccessExcludePath /usr/bin/clamsubmit
OnAccessExcludePath /usr/bin/freshclam
OnAccessExcludePath /usr/bin/sigtool
OnAccessExcludePath /usr/lib/systemd/system/clamav-clamonacc.service
OnAccessExcludePath /usr/lib/systemd/system/clamav-freshclam.service
OnAccessExcludePath /usr/lib/systemd/system/clamd@.service
OnAccessExcludePath /usr/lib/systemd/system/clamonacc.service
OnAccessExcludePath /usr/lib/tmpfiles.d/clamd.scan.conf
OnAccessExcludePath /usr/lib64/libclamav.so.9
OnAccessExcludePath /usr/lib64/libclammspack.so.0
OnAccessExcludePath /usr/lib64/libfreshclam.so.2
OnAccessExcludePath /usr/sbin/clamd
OnAccessExcludePath /sbin/clamd
OnAccessExcludePath /usr/sbin/clamonacc
OnAccessExcludePath /sbin/clamonacc
OnAccessExcludePath /var/lib/clamav
OnAccessExcludePath /var/spool/quarantine

# exclude SELinux related file/dir
OnAccessExcludePath /etc/dbus-1/system.d/org.selinux.conf
OnAccessExcludePath /etc/pam.d/polkit-1
OnAccessExcludePath /etc/polkit-1
OnAccessExcludePath /etc/selinux
OnAccessExcludePath /etc/sestatus.conf
OnAccessExcludePath /etc/sysconfig/selinux
OnAccessExcludePath /usr/bin/audit2allow
OnAccessExcludePath /usr/bin/audit2why
OnAccessExcludePath /usr/bin/chcat
OnAccessExcludePath /usr/bin/pkaction
OnAccessExcludePath /usr/bin/pkcheck
OnAccessExcludePath /usr/bin/pkexec
OnAccessExcludePath /usr/bin/pkla-admin-identities
OnAccessExcludePath /usr/bin/pkla-check-authorization
OnAccessExcludePath /usr/bin/pkttyagent
OnAccessExcludePath /usr/bin/secon
OnAccessExcludePath /usr/bin/semodule_expand
OnAccessExcludePath /usr/bin/semodule_link
OnAccessExcludePath /usr/bin/semodule_package
OnAccessExcludePath /usr/bin/semodule_unpackage
OnAccessExcludePath /usr/bin/sestatus
OnAccessExcludePath /usr/lib/polkit-1
OnAccessExcludePath /usr/lib/rpm/macros.d/macros.selinux-policy
OnAccessExcludePath /usr/lib/systemd/system-generators/selinux-autorelabel-generator.sh
OnAccessExcludePath /usr/lib/systemd/system/polkit.service
OnAccessExcludePath /usr/lib/systemd/system/selinux-autorelabel-mark.service
OnAccessExcludePath /usr/lib/systemd/system/selinux-autorelabel.service
OnAccessExcludePath /usr/lib/systemd/system/selinux-autorelabel.target
OnAccessExcludePath /usr/lib/systemd/system/selinux-check-proper-disable.service
OnAccessExcludePath /usr/lib/tmpfiles.d/selinux-policy.conf
OnAccessExcludePath /usr/lib64/girepository-1.0/Polkit-1.0.typelib
OnAccessExcludePath /usr/lib64/girepository-1.0/PolkitAgent-1.0.typelib
OnAccessExcludePath /usr/lib64/libpolkit-agent-1.so.0
OnAccessExcludePath /usr/lib64/libpolkit-gobject-1.so.0
OnAccessExcludePath /usr/lib64/libpolkit-qt5-agent-1.so.1
OnAccessExcludePath /usr/lib64/libpolkit-qt5-core-1.so.1
OnAccessExcludePath /usr/lib64/libpolkit-qt5-gui-1.so.1
OnAccessExcludePath /usr/libexec/selinux
OnAccessExcludePath /usr/sbin/fixfiles
OnAccessExcludePath /usr/sbin/genhomedircon
OnAccessExcludePath /usr/sbin/load_policy
OnAccessExcludePath /usr/sbin/restorecon
OnAccessExcludePath /usr/sbin/restorecon_xattr
OnAccessExcludePath /usr/sbin/semanage
OnAccessExcludePath /usr/sbin/semodule
OnAccessExcludePath /usr/sbin/sestatus
OnAccessExcludePath /usr/sbin/setfiles
OnAccessExcludePath /usr/sbin/setsebool
OnAccessExcludePath /var/lib/polkit-1
OnAccessExcludePath /var/lib/selinux/targeted

# exclude isolated dir
OnAccessExcludePath ${__ISOLATED_DIR}

# exclude dnf cache dir
OnAccessExcludePath /var/cache/dnf

# exclude kernel source dir
OnAccessExcludePath /usr/src/kernels

#-------------------------------------------------------------------------------
# OnAccessIncludePath / OnAccessExcludePath custom configurations
#-------------------------------------------------------------------------------
#OnAccessIncludePath /var/www
#OnAccessExcludePath /opt/eclipse

#-------------------------------------------------------------------------------
# Enables On-Access Prevention and Extra Scanning
#-------------------------------------------------------------------------------
OnAccessPrevention yes
OnAccessExtraScanning yes

#-------------------------------------------------------------------------------
# OnAccessMountPath
#-------------------------------------------------------------------------------
# If set OnAccessMountPath then OnAccessIncludePath, OnAccessExcludePath,
# OnAccessPrevention and OnAccessExtraScanning options are ignored.
#OnAccessMountPath /

#-------------------------------------------------------------------------------
# Enables On-Access Scanning (since v0.102.0)
#-------------------------------------------------------------------------------
OnAccessExcludeUname clamscan
__EOF

# set user/group to /var/log/clamd.scan
echo Setting clamscan user/group to /var/log/clamd.scan
if [ ! -e /var/log/clamd.scan ]; then
  touch /var/log/clamd.scan
fi
chown clamscan:clamscan /var/log/clamd.scan

# create isolated directory
echo Creating isolated directory ...
mkdir -p ${__ISOLATED_DIR}
chown -R clamscan:clamscan ${__ISOLATED_DIR}

# SELinux boolean value
echo Setting SELinux boolean value ...

setsebool -P antivirus_can_scan_system 1

# install my-antivirus-daemon SELinux package
echo Installing my-antivirus-daemon SELinux package ...

cat << __EOF > /tmp/my-antivirus-daemon.te
module my-antivirus-daemon 1.0;
require {
  attribute antivirus_domain;
  attribute antivirus_t;
  attribute file_type;
  attribute non_security_file_type;
  attribute var_log_t;
  class blk_file { getattr ioctl lock open read };
  class chr_file { getattr ioctl lock open read };
  class file setattr;
  # For running clamonacc in Unit file.
  class cap_userns sys_ptrace;
}

#============= antivirus_t ==============
allow antivirus_domain { file_type non_security_file_type }:blk_file { getattr ioctl lock open read };
allow antivirus_domain { file_type non_security_file_type }:chr_file { getattr ioctl lock open read };
allow antivirus_t var_log_t:file setattr;
# For running clamonacc in Unit file.
allow antivirus_t self:cap_userns sys_ptrace;
__EOF

checkmodule -m -o /tmp/my-antivirus-daemon.mod /tmp/my-antivirus-daemon.te
semodule_package -o /tmp/my-antivirus-daemon.pp -m /tmp/my-antivirus-daemon.mod
semodule -i /tmp/my-antivirus-daemon.pp

rm -f /tmp/my-antivirus-daemon.te /tmp/my-antivirus-daemon.mod /tmp/my-antivirus-daemon.pp

# install my-antivirus-sudo SELinux package
echo Installing my-antivirus-sudo SELinux package ...

cat << __EOF > /tmp/my-antivirus-sudo.te
module my-antivirus-sudo 1.0;
require {
  attribute antivirus_t;
  attribute sudo_exec_t;
  attribute chkpwd_exec_t;
  attribute local_login_t;
  class file { execute execute_no_trans map };
  class capability sys_resource;
  class netlink_audit_socket create;
  class process { setrlimit signull };
}

#============= antivirus_t ==============
# allow execute sudo command by VirusEvent setting.
allow antivirus_t sudo_exec_t:file { execute execute_no_trans map };
allow antivirus_t chkpwd_exec_t:file { execute execute_no_trans map };
allow antivirus_t self:capability sys_resource;
allow antivirus_t self:netlink_audit_socket create;
allow antivirus_t self:process setrlimit;
allow antivirus_t local_login_t:process signull;
__EOF

checkmodule -m -o /tmp/my-antivirus-sudo.mod /tmp/my-antivirus-sudo.te
semodule_package -o /tmp/my-antivirus-sudo.pp -m /tmp/my-antivirus-sudo.mod
semodule -i /tmp/my-antivirus-sudo.pp

rm -f /tmp/my-antivirus-sudo.te /tmp/my-antivirus-sudo.mod /tmp/my-antivirus-sudo.pp

# create symbolic lync
echo Creating /etc/clamd.conf symbolic link ...

(
  cd /etc
  ln -s clamd.d/scan.conf clamd.conf
)

# fs.inotify.max_user_watches to sysctl.conf
if [ `cat /proc/sys/fs/inotify/max_user_watches` -lt 524288 ]; then \
  echo Setting fs.inotify.max_user_watches ...
  echo "fs.inotify.max_user_watches = 524288" >> /etc/sysctl.conf
fi

# enable freshclam  and clam@scan service
echo Enabling freshclam and clam@scan services ...

systemctl enable clamav-freshclam
systemctl enable clamd@scan
if [ -f /usr/lib/systemd/system/clamonacc.service ]; then
  systemctl enable clamonacc
fi

# update virus database
echo Updating virus database ...
freshclam

# start clamav-freshclam, clamd@scan and clanonacc service
echo Starting clamav-freshclam service ...
systemctl start clamav-freshclam
echo Starting clamd@scan service ...
systemctl start clamd@scan
if [ -f /usr/lib/systemd/system/clamonacc.service ]; then
  echo Starting clanonacc service ...
  systemctl start clamonacc
fi
