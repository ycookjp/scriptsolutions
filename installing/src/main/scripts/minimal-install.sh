#!/bin/bash
################################################################################
# Name    : minimal-install.sh
# Usage   : minimal-install.sh [-d {xfce|lxde|mate}] [-s <size>] [-v] [-a] [-h]
################################################################################

# distribution name and virsion
distroname=`uname -r | sed 's/[^a-z^A-Z]*\.\([a-zA-Z]*\).*$/\1/'`
distrover=`uname -r | sed 's/[^a-z^A-Z]*[a-zA-Z]*\([0-9]*\).*$/\1/'`
echo distroname: $distroname
echo distrover: $distrover

## parse option ##
while getopts d:u:s:vah OPT
do
  case $OPT in
    d)
      __DESKTOP=$OPTARG
      ;;
    u)
      __USERNAME=$OPTARG
      ;;
    s)
      __SWAPSIZE=$OPTARG
      ;;
    v)
      __VBOXGA=gcc
      if [ $distroname == fc -a $distrover -ge 35 ]; then
        __VBOXGA=vboxga
      fi
      ;;
    a)
      __AUDIO_ENABLE=yes
      ;;
    h|*)
      echo "Usage: `basename $0` [-d {xfce|lxde|mate}] [-u <username>] [-s <swap-size>]"
      echo "       [-v] [-a] [-h]"
      echo "    -d {xfce|lxde|mate}: Install desktop environment"
      echo "    -u <username>: login user name"
      echo "    -s <swap-size>: zram swap size like as 2048M"
      echo "    -v: Install VirtualBox Guest Additions dependency"
      echo "    -a: Enable audio"
      exit
      ;;
  esac
done
shift $(($OPTIND - 1))

echo "desktop environment: $__DESKTOP"
echo "user name: $__USERNAME"
echo "zram swap size: $__SWAPSIZE"
echo "vbox guest additions: $__VBOXGA"
echo "audio enable: $__AUDIO_ENABLE"

## check options ##
if [ _${__DESKTOP} != _ ]; then
  __found=0
  for __name in xfce lxde mate; do
    if [ _${__DESKTOP} == _${__name} ]; then
      __found=1
    fi
  done
  if [ $__found -eq 0 ]; then
    echo "***** OPTION ERROR *****"
    echo "-d  must be specified one of xfce, lxde, mate"
    echo "***** OPTION ERROR *****"
    exit 1
  fi 
fi

if [ $distroname == el -a $distrover == 8 -a _$__DESKTOP == _mate \
     -o $distroname == el -a $distrover -ge 8 -a _$__DESKTOP == _lxde ]; then
  echo "***** OPTION ERROR *****"
  echo mate or lxde can not install to Redhat EL or CentOS ver $distrover
  echo "************************"
  exit 1
fi

if [ _${__USERNAME} != _ ]; then
  if [ `grep ${__USERNAME} /etc/passwd | wc -l` -eq 0 ]; then
    echo "***** OPTION ERROR *****"
    echo "user ${__USERNAME} not exists"
    echo "***** OPTION ERROR *****"
    exit 1
  fi
fi

read -p "Installing packages. Hit any key to continue." -n 1; echo

################################################################################
# CONFIFURING
################################################################################

# package command
pkgcmd=dnf
upgradecmd="dnf upgrade -y"
if [ $distroname == el -a $distrover -lt 8 ]; then
  pkgcmd=yum
  upgradecmd="yum update -y"
fi

base_packages='rsyslog bash-completion avahi nss-mdns tar bzip2'

# desktop packages
desktopbase_packages='im-chooser ibus-anthy google-noto-*-cjk-*fonts 
    network-manager-applet @networkmanager-submodules xrdp xrdp-selinux 
    gkrellm'

if [ $distroname == fc -a $distrover -le 35 -o $distroname == el -a $distrover -le 8 ]; then
  desktopbase_packages="$desktopbase_packages python36"
fi

xfce_packages='xfce4-panel xfce4-session xfce4-settings xfdesktop xfwm4 
    xfce4-terminal Thunar xfce4-screensaver'
if [ $distroname = fc -o $distroname == el -a $distrover -le 8 ]; then
  xfce_packages="$xfce_packages xfce4-notifyd"
fi
lxde_packages='lxde-common lxpanel lxsession lxpolkit lxappearance lxrandr 
    lxterminal lxdm pcmanfm xscreensaver-base notification-daemon'
mate_packages='mate-panel mate-session-manager mate-terminal marco caja 
    mate-screensaver mate-notification-daemon'

# VirtualBox Guest Additions
if [ _${__VBOXGA} == _vboxga ]; then
  vboxga_packages=virtualbox-guest-additions
else
  vboxga_packages='kernel-devel gcc make perl'
  if [ $distroname == fc -a $distrover -ge 27 -o $distroname == el -a $distrover -ge 8 ]; then
    vboxga_packages="$vboxga_packages elfutils-libelf-devel"
  fi
  if [ $distroname == fc -a $distrover -ge 30 ]; then
    vboxga_packages="$vboxga_packages libxcrypt-compat"
  fi
fi

packages=$base_packages

case "$__DESKTOP" in
  "xfce")
    packages="$packages $desktopbase_packages $xfce_packages"
    start_desktop=startxfce4
    ;;
  "lxde")
    packages="$packages $desktopbase_packages $lxde_packages"
    start_desktop=startlxde
    ;;
  "mate")
    packages="$packages $desktopbase_packages $mate_packages"
    start_desktop=mate-session
    ;;
esac

if [ _${__VBOXGA} != _ ]; then
  packages="$packages $vboxga_packages"
fi

################################################################################
# INSTALLING
################################################################################

## install epel-release when distribution is el
if [ $distroname == el ]; then
  echo "*** installing epel repository ***"
  $pkgcmd install -y epel-release
  if [ $? -ne 0 ]; then exit; fi
fi

## upgrade packages ##
echo "*** upgrading packages ***"
$upgradecmd
if [ $? -ne 0 ]; then exit; fi

## install packages ##
echo "*** installing packages ***"
$pkgcmd install -y $packages
if [ $? -ne 0 ]; then exit; fi

## mDNS settings ##
firewall-cmd --permanent --add-service mdns

if [ ! -f /etc/nsswitch.conf.orig ]; then
  cp -dp /etc/nsswitch.conf /etc/nsswitch.conf.orig
fi
sed 's/\(^hosts:.*\)_minimal .*\( dns .*$\)/\1\2/g' -i /etc/nsswitch.conf

if [ ! -f /usr/lib/systemd/system/avahi-daemon.service.orig ]; then
  cp -dp /usr/lib/systemd/system/avahi-daemon.service /usr/lib/systemd/system/avahi-daemon.service.orig
fi
if [ `grep -i '^After=.*' /usr/lib/systemd/system/avahi-daemon.service | wc -l` -gt 0 ]; then
  sed 's/^After.*$/& network-online.target/g' -i /usr/lib/systemd/system/avahi-daemon.service
else
  sed 's/\n\[Service\]/After=network-online.target\n&/g' -i /usr/lib/systemd/system/avahi-daemon.service
fi

systemctl daemon-reload
systemctl enable --now avahi-daemon

## xpdp settings ##
if [ ! -f /etc/xrdp/xrdp.ini.orig ]; then
  cp -dp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.orig
fi
sed 's/\(^max_bpp=\).*$/#&\n\124/g' -i /etc/xrdp/xrdp.ini

if [ ! -f /etc/xrdp/sesman.ini.orig ]; then
  cp -dp /etc/xrdp/sesman.ini /etc/xrdp/sesman.ini.orig
fi
sed 's/\(^AllowRootLogin=\).*$/#&\n\1false/g' -i /etc/xrdp/sesman.ini

if [ _${__DESKTOP} != _ ]; then
  firewall-cmd --permanent --add-port 3389/tcp

  echo $start_desktop > /etc/skel/.Xclients
  chmod +x /etc/skel/.Xclients
  if [ _${__USERNAME} != _ ]; then
    sudo su ${__USERNAME} -c "cp -f /etc/skel/.Xclients ~/"
  fi

  systemctl enable --now xrdp
fi

if [ _${__DESKTOP} == _xfce ]; then
  if [ ! -f /usr/share/applications/im-chooser.desktop.orig ]; then
    cp -dp /usr/share/applications/im-chooser.desktop /usr/share/applications/im-chooser.desktop.orig
  fi
  sed 's/^NotShowIn=.*XFCE.*$/#&/g' -i /usr/share/applications/im-chooser.desktop
fi

## virtualbox-guest-additions settings ##
if [ _${__USERNAME} != _ -a _${__VBOXGA} == _vboxga ]; then
  usermod -aG vboxsf ${__USERNAME}
fi

## zram swap configuration ##
if [ _${__SWAPSIZE} != _ ]; then
  if [ -f /usr/lib/systemd/zram-generator.conf ]; then
    echo "*** skipping zram configuration. ***"
    echo "*** /usr/lib/systemd/zram-generator.conf exists. ***"
  else
    echo "zram" > /etc/modules-load.d/zram.conf
    echo "options zram num_devices=1" > /etc/modprobe.d/zram.conf
    cat << __EOF > /usr/lib/systemd/system/zram.service
[Unit]
Description=Swap with zram
After=basic.target

[Service]
Type=oneshot 
RemainAfterExit=true
ExecStartPre=/sbin/zramctl /dev/zram0 --size ${__SWAPSIZE}
ExecStartPre=/sbin/mkswap /dev/zram0
ExecStart=/sbin/swapon /dev/zram0
ExecStop=/sbin/swapoff /dev/zram0

[Install]
WantedBy=multi-user.target
__EOF
    systemctl enable zram.service
    echo -e "zram swap generated.\ncheck /etc/fstab not to exists swap entry."
  fi
fi

## Pulse Audio
if [ _${__AUDIO_ENABLE} ]; then
  if [ $distroname == fc -a $distrover -ge 34 -o \
       $distroname == el -a $distrover -ge 9 ]; then
    $pkgcmd install -y pipewire-pulseaudio pavucontrol alsa-firmware
  else
    $pkgcmd install -y alsa-plugins-pulseaudio pavucontrol alsa-firmware
  fi
  if [ _${__USERNAME} != _ ]; then
    usermod -aG audio ${__USERNAME}
  fi
fi

## reload firewalld ##
firewall-cmd --reload
