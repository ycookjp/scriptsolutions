#!/bin/sh

################################################################################
# Name    : fedora35-container-base
# Usage   : fedora35-container-base.sh
# Run CMD : /bin/bash
# Depends : dnf.conf
# Creating image :
#   1. Start Fedora 35 and login as root.
#   2. Place this file and dependencies at same directory.
#   3. Edit dnf.conf to configure proxy setting.
#   4. Run this script.
#   5. Move to docker-images/fedora35-container-base directory and run
#      "tar -c . | docker import - fedora35-container-base" command.
################################################################################

if [ _ = _${DOCKER_IMAGE} ]; then
  export DOCKER_IMAGE=`basename -s .sh $0`
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

# Additional packages
ADDITIONAL_PACKAGES=""

## Installing Fedora Minimal Install
mkdir -p ${INSTALL_ROOT}/etc/yum.repos.d
dnf --installroot=${INSTALL_ROOT} --config=${DNF_CONFIG} \
    --setopt=reposdir=${INSTALL_ROOT}/etc/yum.repos.d \
    --releasever ${RELEASE_VER} --forcearch=${BASE_ARCH} \
    install -y \
      --exclude=glibc-all-langpacks \
      basesystem \
      bash \
      coreutils-single \
      curl \
      dnf \
      filesystem \
      glibc \
      glibc-langpack-en \
      glibc-minimal-langpack \
      grubby \
      kbd \
      langpacks-en \
      ncurses-base \
      rootfiles \
      rpm \
      setup \
      sssd-client \
      systemd \
      tar \
      util-linux \
      vim-minimal

## Setting Proxy URL
if [ _ != _${PROXY_URL} ]; then
  export http_proxy=${PROXY_URL} https_proxy=${PROXY_URL}
fi

## Installing additional packages
if [ "" != "${ADDITIONAL_PACKAGES}" ]; then
  dnf --installroot=${INSTALL_ROOT} install -y ${ADDITIONAL_PACKAGES}
fi

## Removing package cache
dnf --installroot=${INSTALL_ROOT} --releasever ${RELEASE_VER} clean all
