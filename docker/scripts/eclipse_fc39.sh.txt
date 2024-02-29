#!/bin/sh

################################################################################
# Name    : eclipse-<desktop_env>
# Usage   : DESKTOP_ENV={xfce|mate} eclipse_fc39.sh
# Depends : desktop_fc39.sh, fedora39-container-base.sh, dnf.conf
# Creating image :
#   1. Start Fedora 39 and login as root.
#   2. Place this file and dependencies at same directory.
#   3. Edit dnf.conf to configure proxy setting.
#   4. Place following files imported to image.
#     --------------------------------------------------------------------------
#     import-files
#     |-- eclipse_fc39
#     |   |-- archives (Optional)
#     |   |   `-- *.tar.gz
#     |   `-- files
#     |       `-- etc
#     |           |-- pki
#     |           |   `-- ca-trust
#     |           |       `-- source
#     |           |           `-- anchors
#     |           |               `-- <CA Certificate file(s)>
#     |           `-- skel
#     |               `-- .m2
#     |                   `-- settings.xml
#     `-- download (Optional)
#         |-- eclipse-jee-2023-12-R-linux-gtk-x86_64.tar.gz
#         |-- eclipse-dropins-2023-12.zip
#         `-- migu-1m-20150712.zip
#     --------------------------------------------------------------------------
#     * settings.xml : Maven settings.xml file. You have to configure
#       proxy setting to this file.
#     * eclipse-dropins-yyyy-mm.zip : archiving eclipse dropins plug-in(s).
#       dropins directory must be placed at "dropins".
#   5. Run this script.
#   6. Move to docker-images/eclipse-<desktop_env> directory and run
#      "tar -c . | docker import - <image-name>" command.
# Running :
#   docker run --name=<container-name> --restart={always|unless-stopped} \
#   -p <host-port>:3389 \
#   [--privileged -v <host-workspace-path>:<container-workspace-path>:rw] \
#   -it <image-name> /usr/local/bin/start-xrdp
# Notice:
#   * <container-workspace-path> directory permission shuld be 770.
#   * <container-workspace-path> directory owner/group shuld be specified
#     user ID/group ID defined at container's /etc/passwd, /etc/group files.
################################################################################

if [ _ = _${DESKTOP_ENV} ]; then
  export DESKTOP_ENV=lxde
fi
if [ _ = _${DOCKER_IMAGE} ]; then
  export DOCKER_IMAGE=`basename -s .sh $0`-${DESKTOP_ENV}
fi
if [ _ = _${RELEASE_VER} ]; then
  export RELEASE_VER=39
fi
if [ _ = _${BASE_ARCH} ]; then
  export BASE_ARCH=x86_64
fi

INSTALL_ROOT=`pwd`/docker-images/${DOCKER_IMAGE}
if [ _ = _${DNF_CONFIG} ]; then
  export DNF_CONFIG=`dirname $0`/dnf.conf
fi
PROXY_URL=`grep -e '^proxy=' ${DNF_CONFIG} | sed 's/^proxy=//g'`

export CONTENTS_DIR=`pwd`/import-files/`basename -s .sh $0`

if [ _ = _${DOWNLOAD_DIR} ]; then
  export DOWNLOAD_DIR=${CONTENTS_DIR}/../download
fi

## Installing Fedora Desktop
`dirname $0`/desktop_fc${RELEASE_VER}.sh

# Eclispe IDE for Enterprise Java Developers
ECLIPSE_URL=https://ftp.yz.yamagata-u.ac.jp/pub/eclipse//technology/epp/downloads/release/2023-12/R/eclipse-jee-2023-12-R-linux-gtk-x86_64.tar.gz

# Eclipse Dropins archive
ECLIPSE_DROPINS_FILE=eclipse-dropins-2023-12.zip

# migu font
MIGU_URL=https://osdn.jp/projects/mix-mplus-ipa/downloads/63545/migu-1m-20150712.zip

## Creating download temporary directory
mkdir -p ${DOWNLOAD_DIR}

## Setting Proxy URL
if [ _ != _${PROXY_URL} ]; then
  export http_proxy=${PROXY_URL} https_proxy=${PROXY_URL}
fi
if [ _ != _${PROXY_URL} ]; then
  OPT_CURL_PROXY="-x ${PROXY_URL}"
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
    tar -xvz -f $f -C ${INSTALL_ROOT} --overwrite --no-same-owner --no-same-permissions; \
  done
fi

## Installing openjdk
dnf --installroot=${INSTALL_ROOT} install -y java-11-openjdk-devel webkit2gtk3

## Downloadomg and installing eclipse
if [ _ != _${ECLIPSE_URL} ]; then
  if [ ! -f ${DOWNLOAD_DIR}/`basename ${ECLIPSE_URL}` ]; then
    curl ${OPT_CURL_PROXY} --create-dirs -L ${ECLIPSE_URL} -o ${DOWNLOAD_DIR}/`basename ${ECLIPSE_URL}`
  fi
  mkdir -p ${INSTALL_ROOT}/opt
  tar -xvz -f ${DOWNLOAD_DIR}/`basename ${ECLIPSE_URL}` -C ${INSTALL_ROOT}/opt --overwrite --no-same-owner --no-same-permissions

## Creating eclipse menu entry
  mkdir -p ${INSTALL_ROOT}/usr/share/applications
  chroot ${INSTALL_ROOT} echo -e '[Desktop Entry]
Version=1.0
Type=Application
Name=Eclipse
GenericName=Java IDE
Comment=Eclipse Java IDE
Icon=/opt/eclipse/icon.xpm
Categories=GTK;Development;IDE;
Exec=/opt/eclipse/eclipse %U
TryExec=/opt/eclipse/eclipse' \
> ${INSTALL_ROOT}/usr/share/applications/eclipse.desktop
fi

## Installing Eclipse Dropins
if [ _ != _${ECLIPSE_DROPINS_FILE} ]; then
  if [ -f ${DOWNLOAD_DIR}/`basename ${ECLIPSE_DROPINS_FILE}` ]; then
    unzip -o -d ${INSTALL_ROOT}/opt/eclipse ${DOWNLOAD_DIR}/`basename ${ECLIPSE_DROPINS_FILE}`;
  fi
fi

## Downloading and installing migu font
if [ _ != _${MIGU_URL} ]; then
  if [ ! -f ${DOWNLOAD_DIR}/`basename ${MIGU_URL}` ]; then
    curl ${OPT_CURL_PROXY} --create-dirs -L ${MIGU_URL} -o ${DOWNLOAD_DIR}/`basename ${MIGU_URL}`
  fi
  chroot ${INSTALL_ROOT} mkdir -p /usr/share/fonts
  unzip -o -d ${INSTALL_ROOT}/usr/share/fonts ${DOWNLOAD_DIR}/`basename ${MIGU_URL}`
  chroot ${INSTALL_ROOT} rm -rf \
         /usr/share/fonts/migu-1m-20150712/ipag00303/\
         /usr/share/fonts/migu-1m-20150712/mplus-TESTFLIGHT-060/\
         /usr/share/fonts/migu-1m-20150712/*.txt
fi

## Removing package cache
dnf --installroot=${INSTALL_ROOT} --releasever ${RELEASE_VER} clean all
