#!/bin/sh

################################################################################
# Name    : httpd-svn
# Usage   : fedora34-httpd-svn.sh
# Depends : fedora34-container-base.sh, dnf.conf
# Creating image :
#   1. Start Fedora 34 and login as root.
#   2. Place this file and dependencies at same directory.
#   3. Edit dnf.conf to configure proxy setting.
#   4. Run this script.
#   5. Move to docker-images/httpd-svn directory and run
#      "tar -c . | docker import - <image-name>" command.
# Running :
#   docker run --name <container-name> --restart=always -p <host-port>:80 \
#   -it <image-name> /usr/local/bin/start-httpd
#
# Creating new repository:
#   1. Run following commands.
#     cd /var/www/svn
#     svnadmin create <repo-name>
#     chown -R apache:apache <repo-name>
#     restorecon -R <repo-name>
#   2. Add following lines to /etc/httpd/conf.d/svn.conf
#     <Location /svn/<<repo-name>>>
#       Require group <<repo-name>>
#     </Location>
#   3. Add following line to /etc/httpd/conf/htgroup.svn
#     <repo-name>: <<ser-name> <user-name> ...
#
# Adding and deleting user and changing password
#   1. Adding user, changing password
#     htpasswd -b[c] /etc/httpd/conf/htpasswd.svn <user-name> <password>
#     * If htpasswd.svn not exists, specify -c option.
#   2. Deleting user
#     htpasswd -D /etc/httpd/conf/htpasswd.svn <user-name>
################################################################################

if [ _ = _${DOCKER_IMAGE} ]; then
  export DOCKER_IMAGE=`basename -s .sh $0`
fi
if [ _ = _${RELEASE_VER} ]; then
  export RELEASE_VER=34
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
BASE_PACKAGES="httpd mod_dav_svn mod_ssl subversion langpacks-ja"
BUILD_PACKAGES=""

## Installing Fedora Minimal Install
`dirname $0`/fedora${RELEASE_VER}-container-base.sh

## Setting Proxy URL
if [ _ != _${PROXY_URL} ]; then
  export http_proxy=${PROXY_URL} https_proxy=${PROXY_URL}
fi

## Installing base packages
dnf --installroot=${INSTALL_ROOT} install -y ${BASE_PACKAGES}

## Generating certs
chroot ${INSTALL_ROOT} /usr/libexec/httpd-ssl-gencerts

## Japanese language settings
if [ "" != "`echo ${BASE_PACKAGES} ${BUILD_PACKAGES} | grep 'langpacks-ja'`" ]; then
  ## Setting localtime
  chroot ${INSTALL_ROOT} ln -sf ../usr/share/zoneinfo/Asia/Tokyo /etc/localtime
  ## Setting the System Locale
  chroot ${INSTALL_ROOT} echo LANG="ja_JP.UTF-8" > ${INSTALL_ROOT}/etc/locale.conf
fi

## Generating docker run script
chroot ${INSTALL_ROOT} echo -e '#!/bin/sh

trap "/usr/sbin/httpd -k stop" SIGHUP SIGTERM
/usr/sbin/httpd
while [ \`ps h -C httpd | wc -l\` -gt 0 ]; do sleep 2; done
echo /usr/sbin/httpd stopped.
exit' \
> ${INSTALL_ROOT}/usr/local/bin/start-httpd
chroot ${INSTALL_ROOT} chmod a+x /usr/local/bin/start-httpd

## Generating proxy configuration
chroot ${INSTALL_ROOT} echo -e '<Location /svn>
  DAV svn
  SVNParentPath /var/www/svn
  AuthType Basic
  AuthName "Subversion repository"
  AuthUserFile /etc/httpd/conf/htpasswd.svn
  AuthGroupFile /etc/httpd/conf/htgroup.svn
</Location>' \
> ${INSTALL_ROOT}/etc/httpd/conf.d/svn.conf

## Create repository parent directory
chroot ${INSTALL_ROOT} mkdir -p /var/www/svn
chroot ${INSTALL_ROOT} chown apache:apache /var/www/svn
# SELinux settings
: #semanage fcontext -m -t httpd_sys_content_t "/var/www/svn(/.*)?"
: #semanage fcontext -a -t httpd_sys_script_exec_t "/var/www/svn/[^/]+/hooks(/.*)?"
: #semanage fcontext -a -t httpd_sys_rw_content_t "/var/www/svn/[^/]+/db/txn-current-lock"
: #restorecon -R /var/www/svn/
: #setsebool -p httpd_unified 1

## Removing package cache
dnf --installroot=${INSTALL_ROOT} --releasever ${RELEASE_VER} clean all
