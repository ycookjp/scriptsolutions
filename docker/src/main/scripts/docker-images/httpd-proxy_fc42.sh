#!/bin/sh

################################################################################
# Name    : httpd-proxy
# Usage   : httpd-proxy_fc42.sh <ipaddress>/<netmask>
#   * <ipaddress> and <netmask> : "Allow from" network.
# Depends : fedora-container-base_fc42.sh, dnf.conf
# Creating image :
#   1. Start Fedora 42 and login as root.
#   2. Place this file and dependencies at same directory.
#   3. Edit dnf.conf to configure proxy setting.
#   4. Run this script.
#   5. Move to docker-images/httpd-proxy directory and run
#      "tar -c . | docker import - <image-name>" command.
# Running :
#   docker run --name <container-name> --restart=always -p <host-port>:80 \
#   -it <image-name> /usr/local/bin/start-httpd
################################################################################

if [ $# -eq 0 ]; then
  echo "Usage `basename $0` allow_from_network"
  echo "allow_from_network : ipaddress/netmask or ipaddress/nnn"
  exit
fi

if [ _ = _${DOCKER_IMAGE} ]; then
  export DOCKER_IMAGE=`basename -s .sh $0`
fi
if [ _ = _${RELEASE_VER} ]; then
  export RELEASE_VER=42
fi
if [ _ = _${BASE_ARCH} ]; then
  export BASE_ARCH=x86_64
fi

INSTALL_ROOT=`pwd`/docker-images/${DOCKER_IMAGE}
if [ _ = _${DNF_CONFIG} ]; then
  export DNF_CONFIG=`dirname $0`/dnf.conf
fi
PROXY_URL=`grep -e '^proxy=' ${DNF_CONFIG} | sed 's/^proxy=//g'`

# install packages
BASE_PACKAGES="httpd mod_ssl langpacks-ja"
BUILD_PACKAGES=""

# allowing network
PROXY_ALLOW_FROM=$1

## Installing Fedora Minimal Install
`dirname $0`/fedora-container-base_fc${RELEASE_VER}.sh

## Setting Proxy URL
if [ _ != _${PROXY_URL} ]; then
  export http_proxy=${PROXY_URL} https_proxy=${PROXY_URL}
fi

## Installing Fedora Desktop and xrdp
dnf --installroot=${INSTALL_ROOT} install -y ${BASE_PACKAGES}

## Generating certs
chroot ${INSTALL_ROOT} /usr/libexec/httpd-ssl-gencerts

## Japanese language settings
if [ "" != "`echo ${BASE_PACKAGES} ${BUILD_PACKAGES} | grep 'langpacks-ja'`" ]; then
  ## Setting localtime
  chroot ${INSTALL_ROOT} ln -sf ../usr/share/zoneinfo/Asia/Tokyo /etc/localtime
  ## Setting the System Locale
  echo LANG="ja_JP.UTF-8" > ${INSTALL_ROOT}/etc/locale.conf
fi

## Generating docker run script
chroot ${INSTALL_ROOT} echo -e '#!/bin/sh

trap "/usr/sbin/httpd -k stop" SIGHUP SIGTERM
/usr/sbin/httpd
while [ `ps h -C httpd | wc -l` -gt 0 ]; do sleep 2; done
echo /usr/sbin/httpd stopped.
exit' \
> ${INSTALL_ROOT}/usr/local/bin/start-httpd
chroot ${INSTALL_ROOT} chmod a+x /usr/local/bin/start-httpd

## Generating proxy configuration
chroot ${INSTALL_ROOT} echo -e "<IFModule mod_proxy.c>
  ProxyRequests On
  ProxyVia On

  <Proxy *>
    Order deny,allow
    Deny from all
    Allow from ${PROXY_ALLOW_FROM}
  </Proxy>
</IFModule>" \
> ${INSTALL_ROOT}/etc/httpd/conf.d/mod_proxy.conf

## Removing package cache
dnf --installroot=${INSTALL_ROOT} --releasever ${RELEASE_VER} clean all
