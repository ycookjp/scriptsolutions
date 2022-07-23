#!/bin/sh

################################################################################
# Name    : fedora-<desktop_env>
# Usage   : DESKTOP_ENV={lxde|mate|xfce} [GROUP_ID=<gid>] fedora35-desktop.sh
# Depends : fedora35-container-base.sh, dnf.conf
# Creating image :
#   1. Start Fedora 35 and login as root.
#   2. Place this file and dependencies at same directory.
#   3. Edit dnf.conf to configure proxy setting.
#   4. Place following files imported to image.
#     --------------------------------------------------------------------------
#     import-files
#     `-- download (Optional)
#         |-- Windows.10.Dark.v0.9.9.SP1.tar.gz
#         `-- Windows.10.Icons.v0.5.tar.gz
#     --------------------------------------------------------------------------
#   5. Run this script.
#   6. Move to docker-images/fedora-<desktop_env> directory and run
#      "tar -c . | docker import - <image-name>" command.
# Running :
#   docker run --name=<container-name> --restart={always|unless-stopped} \
#   -p <host-port>:3389 -it <image-name> /usr/local/bin/start-xrdp
################################################################################

if [ _ = _${DESKTOP_ENV} ]; then
  #DESKTOP_ENV=cinnamon
  #DESKTOP_ENV=gnome
  #DESKTOP_ENV=kde
  DESKTOP_ENV=lxde
  #DESKTOP_ENV=mate
  #DESKTOP_ENV=xfce
fi

if [ _ = _${GROUP_ID} ]; then
  GROUP_ID=1000
fi

if [ _ = _${DOCKER_IMAGE} ]; then
  export DOCKER_IMAGE=`basename -s .sh $0`-${DESKTOP_ENV}
fi
if [ _ = _${RELEASE_VER} ]; then
  export RELEASE_VER=35
fi
if [ _ = _${BASE_ARCH} ]; then
  export BASE_ARCH=x86_64
fi

INSTALL_ROOT=`pwd`/docker-images/${DOCKER_IMAGE}
if [ _ = _${DNF_CONFIG} ]; then
  export DNF_CONFIG=`dirname $0`/dnf.conf
fi
PROXY_URL=`grep -e '^proxy=' ${DNF_CONFIG} | sed 's/^proxy=//g'`

if [ _ = _${CONTENTS_DIR} ]; then
  export CONTENTS_DIR=`pwd`/import-files/`basename -s .sh $0`
fi

if [ _ = _${DOWNLOAD_DIR} ]; then
  export DOWNLOAD_DIR=${CONTENTS_DIR}/../download
fi

# Installing packages
BASE_PACKAGES="--exclude=elementary-greeter @base-x lightdm im-chooser google-noto-sans-cjk-ttc-fonts google-noto-serif-cjk-ttc-fonts langpacks-ja ibus-kkc net-tools xrdp"
BUILD_PACKAGES="tar unzip passwd"

# Desktop packages
if [ _lxde = _${DESKTOP_ENV} ]; then # LXDE
  DESKTOP_PACKAGES="lxde-common lxpanel lxsession lxpolkit lxappearance lxrandr lxterminal lxdm pcmanfm"
elif [ _mate = _${DESKTOP_ENV} ]; then # mate
  DESKTOP_PACKAGES="mate-panel mate-session-manager mate-terminal marco caja"
elif [ _xfce = _${DESKTOP_ENV} ]; then # Xfce
  DESKTOP_PACKAGES="xfce4-panel xfce4-session xfce4-settings xfdesktop xfwm4 xfce4-terminal Thunar"
else # Cinnamon, Gnome, KDE
  DESKTOP_PACKAGES=@${DESKTOP_ENV}-desktop
fi

if [ "" != "`echo ${BASE_PACKAGES} ${DESKTOP_PACKAGES} ${BUILD_PACKAGES} | grep 'langpacks-ja'`" ]; then
  export LANG=ja_JP.UTF-8
fi

## Installing Fedora Minimal Install
`dirname $0`/fedora${RELEASE_VER}-container-base.sh

# Windows 10 Theme
WIN10THEME_URL=https://github.com/B00merang-Project/Windows-10/releases/download/v0.9.9-AU/Windows.10.Dark.v0.9.9.SP1.tar.gz
# Windos 10 Icons
WIN10ICON_URL=https://github.com/B00merang-Project/Windows-10/releases/download/v0.9.9-AU/Windows.10.Icons.v0.5.tar.gz

## Creating download temporary directory
mkdir -p ${DOWNLOAD_DIR}

## Setting Proxy URL
if [ _ != _${PROXY_URL} ]; then
  export http_proxy=${PROXY_URL} https_proxy=${PROXY_URL}
fi
if [ _ != _${PROXY_URL} ]; then
  OPT_CURL_PROXY="-x ${PROXY_URL}"
fi

## Installing Fedora Desktop and xrdp
dnf --installroot=${INSTALL_ROOT} install -y ${BASE_PACKAGES} ${DESKTOP_PACKAGES} ${BUILD_PACKAGES}

if [ "" != "`echo ${BASE_PACKAGES} ${DESKTOP_PACKAGES} ${BUILD_PACKAGES} | grep 'langpacks-ja'`" ]; then
  ## Setting localtime
  chroot ${INSTALL_ROOT} ln -sf ../usr/share/zoneinfo/Asia/Tokyo /etc/localtime
  ## Setting the System Locale
  echo LANG="ja_JP.UTF-8" > ${INSTALL_ROOT}/etc/locale.conf
fi

## Generating docker run script
chroot ${INSTALL_ROOT} echo -e '#!/bin/sh

trap "/sbin/xrdp -k; /sbin/xrdp-sesman -k" SIGHUP SIGTERM
if [ -f /var/run/xrdp.pid ]; then /sbin/xrdp -k; rm -f /var/run/xrdp.pid; fi
if [ -f /var/run/sesman.pid ]; then /sbin/xrdp-sesman -k; rm -f /var/run/sesman.pid; fi
/sbin/xrdp-sesman
/sbin/xrdp
while [ `ps h -C xrdp-sesman,xrdp | wc -l` -gt 0 ]; do sleep 2; done
echo xrdp service stopped.
exit' \
> ${INSTALL_ROOT}/usr/local/bin/start-xrdp
chroot ${INSTALL_ROOT} chmod a+x /usr/local/bin/start-xrdp

## Modifying xrdp.init max_bpp=32 => max_bpp=24
chroot ${INSTALL_ROOT} sed -e 's/^max_bpp=32/#max_bpp=32\
max_bpp=24/g' -i /etc/xrdp/xrdp.ini

## Creating .Xclients
chroot ${INSTALL_ROOT} mkdir -p /etc/skel
if [ _xfce = _${DESKTOP_ENV} ]; then
  echo "startxfce4" > ${INSTALL_ROOT}/etc/skel/.Xclients
elif [ _kde = _${DESKTOP_ENV} -o _lxde = _${DESKTOP_ENV} ]; then
  echo "start${DESKTOP_ENV}" > ${INSTALL_ROOT}/etc/skel/.Xclients
elif [ _gnome = _${DESKTOP_ENV} -o _mate = _${DESKTOP_ENV} ]; then
  echo "${DESKTOP_ENV}-session" > ${INSTALL_ROOT}/etc/skel/.Xclients
else
  echo "${DESKTOP_ENV}" > ${INSTALL_ROOT}/etc/skel/.Xclients
fi
chroot ${INSTALL_ROOT} chmod +x /etc/skel/.Xclients

## Downloading and installing Windows 10 theme
if [ _ != _${WIN10THEME_URL} ]; then
  if [ ! -f ${DOWNLOAD_DIR}/`basename ${WIN10THEME_URL}` ]; then
    curl ${OPT_CURL_PROXY} --create-dirs -L ${WIN10THEME_URL} -o ${DOWNLOAD_DIR}/`basename ${WIN10THEME_URL}`
  fi
  mkdir -p ${INSTALL_ROOT}/usr/share/themes
  tar --overwrite -xvz -f ${DOWNLOAD_DIR}/`basename ${WIN10THEME_URL}` -C ${INSTALL_ROOT}/usr/share/themes
fi

## Downloading and installing windows 10 icon
if [ _ != _${WIN10ICON_URL} ]; then
  if [ ! -f ${DOWNLOAD_DIR}/`basename ${WIN10ICON_URL}` ]; then
    curl ${OPT_CURL_PROXY} --create-dirs -L ${WIN10ICON_URL} -o ${DOWNLOAD_DIR}/`basename ${WIN10ICON_URL}`
  fi
  mkdir -p ${INSTALL_ROOT}/usr/share/icons
  tar --overwrite -xvz -f ${DOWNLOAD_DIR}/`basename ${WIN10ICON_URL}` -C ${INSTALL_ROOT}/usr/share/icons
fi

## Copying import files
if [ -d ${CONTENTS_DIR}/files ]; then
  mkdir -p ${INSTALL_ROOT}
  cp -R ${CONTENTS_DIR}/files/* ${INSTALL_ROOT}
  # Running update-ca-trust command
  if [ -f ${INSTALL_ROOT}/usr/bin/update-ca-trust ]; then
    chroot ${INSTALL_ROOT} /usr/bin/update-ca-trust extract
  fi
fi
if [ -d ${CONTENTS_DIR}/archives ]; then
  for f in `find ${CONTENTS_DIR}/archives -name '*.tar.gz'`; do \
    tar --overwrite -xvz -f $f -C ${INSTALL_ROOT}; \
  done
fi

## Creating developers group and developer user with password developer
chroot ${INSTALL_ROOT} groupadd -g ${GROUP_ID} developers
chroot ${INSTALL_ROOT} useradd -G developers -p '$6$uR3QShUKOAj.K2gJ$.HkhrYGZLRMW7xEzuRH2K2hkF8C3tvK8xxDpJy/uOHPb7Kv4x.xlDpG8Zz3IvaukTtokPRcDaMHJVpRh1EHed.' developer
#chroot ${INSTALL_ROOT} usermod -p '$6$uR3QShUKOAj.K2gJ$.HkhrYGZLRMW7xEzuRH2K2hkF8C3tvK8xxDpJy/uOHPb7Kv4x.xlDpG8Zz3IvaukTtokPRcDaMHJVpRh1EHed.' developer

## Removing package cache
dnf --installroot=${INSTALL_ROOT} --releasever ${RELEASE_VER} clean all
