#!/bin/bash
################################################################################
# Name    : git-http-install.sh
# Usage   : git-http-install.sh [-n FQDN-hostname]
################################################################################

# parse option
while getopts hn: OPT
do
  case $OPT in
    n)
        __HOSTNAME=$OPTARG
        ;;
    h|*)
        echo "Usage: `basename $0` [-n FQDN-hostname]"
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

# Befire run this script, you have already installed git-lfs-fcgi package.
if [ x${__PKGCMD} = xdns ]; then
  if [ `${__PKGCMD} list -q --installed git-lfs-fcgi | wc -l` -eq 0 ]; then
    read -p "You must install git-lfs-fcgi package. Hit any key to exit." -n 1
    echo; exit
  fi
elif [ `${__PKGCMD} list -q installed git-lfs-fcgi | wc -l` -eq 0 ]; then
  read -p "You must install git-lfs-fcgi package. Hit any key to exit." -n 1
  echo; exit
fi

read -p "Installing git-lfs-fcgi package. Hit any key to continue." -n 1; echo

# install neccesary packages
__PKGLIST="sed checkpolicy policycoreutils"
if [ ${__PKGCMD} = dnf ]; then
  __PKGLIST="${__PKGLIST} policycoreutils-python-utils"
else
  __PKGLIST="${__PKGLIST} policycoreutils-python"
fi
${__PKGCMD} install -y ${__PKGLIST}

# install git and git-lfs packages.
${__PKGCMD} install -y git git-lfs

################################################################################
# Git smart http configuration
################################################################################
# configure /etc/httpd/conf.d/git-smart-http.conf
echo Configuring /etc/httpd/conf.d/git-smart-http.conf ...

cat << __EOF > /etc/httpd/conf.d/git-smart-http.conf
SetEnv GIT_PROJECT_ROOT /var/lib/git
SetEnv GIT_HTTP_EXPORT_ALL
ScriptAlias /git/ /usr/libexec/git-core/git-http-backend/

RewriteEngine On
RewriteCond %{QUERY_STRING} service=git-receive-pack [OR]
RewriteCond %{REQUEST_URI} /git-receive-pack\$
RewriteRule ^/git/ - [E=AUTHREQUIRED]

<Location "/git/">
    AuthType Basic
    AuthName "Git Realm"
    AuthUserFile /etc/httpd/conf/htpasswd.git
    Require valid-user

    # For git-lfs-fcgi authentication
    SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=\$1
</Location>
__EOF

# install my-antivirus-sudo SELinux package
echo Installing my-http-git SELinux package ...

cat << __EOF > /tmp/my-httpd-git.te
module my-httpd-git 1.0;
require {
        type git_sys_content_t;
        type httpd_t;
        type httpd_sys_script_t;
        class file { append create entrypoint execute execute_no_trans getattr ioctl link lock map open read rename setattr unlink write };
        class dir { add_name create getattr ioctl link lock open read remove_name rename reparent rmdir search setattr unlink write };
}
#============= httpd_t ==============
allow httpd_t git_sys_content_t:file { append create execute execute_no_trans getattr ioctl link lock map open read rename setattr unlink write };
allow httpd_t git_sys_content_t:dir { add_name create getattr ioctl link lock open read remove_name rename reparent rmdir search setattr unlink write };
#============= httpd_sys_script_t ==============
allow httpd_sys_script_t git_sys_content_t:file { append create entrypoint execute execute_no_trans getattr ioctl link lock map open read rename setattr unlink write };
allow httpd_sys_script_t git_sys_content_t:dir { add_name create getattr ioctl link lock open read remove_name rename reparent rmdir search setattr unlink write };
__EOF

checkmodule -m -o /tmp/my-httpd-git.mod /tmp/my-httpd-git.te
semodule_package -o /tmp/my-httpd-git.pp -m /tmp/my-httpd-git.mod
semodule -i /tmp/my-httpd-git.pp

rm -f /tmp/my-httpd-git.te /tmp/my-httpd-git.mod /tmp/my-httpd-git.pp

# crate git repository parent directory
mkdir -p /var/lib/git

# create gitusers group and set owner and mode to parent directory
groupadd gitusers
usermod -aG gitusers apache
chmod 775 /var/lib/git
chown apache:gitusers /var/lib/git

# crate example Git repository
git init --bare --shared /var/lib/git/example.git
chown -R apache:gitusers /var/lib/git/example.git
sudo -u apache git config --file /var/lib/git/example.git/config http.receivepack true

# set SELinux label
semanage fcontext -a -t httpd_sys_script_exec_t "/var/lib/git/[^/]*/hooks(/.*)?"
restorecon -R -v /var/lib/git

# set hook scripts
(
  cd /var/lib/git/example.git/hooks
  cp -dpvi post-update.sample post-update
  chmod a+x post-update
)

cat << __EOF > /var/lib/git/example.git/hooks/update
#!/bin/sh
# set allowing users to commit as "<user1> <user2> ..."
adminusers="gituser"
# set ristricted branches to commit as "<branch1> <branch2> ..."
branches="master"

if [ -z \${GIT_COMMITTER_NAME} ]; then
  if [ -n \${USER} ]; then
    GIT_COMMITTER_NAME=\${USER}
  else
    GIT_COMMITTER_NAME=\${REMOTE_USER}
  fi
fi

is_admin=false
for adminuser in \${adminusers}; do
  if [ \${GIT_COMMITTER_NAME} == \${adminuser} ]; then
    is_admin=true
  fi
done
for branchname in \${branches}; do
  if [ \${is_admin} != true -a "\$1" == refs/heads/\${branchname} ]; then
    echo "ERROR: \${GIT_COMMITTER_NAME} are not allowed to update \${branchname}" >&2
    exit 1
  fi
done
__EOF

chown apache:gitusers /var/lib/git/example.git/hooks/update
chmod a+x /var/lib/git/example.git/hooks/update
(
  cd /var/lib/git/example.git/
  sudo -u apache git config --file config http.receivepack true
)


################################################################################
# Git LFS fcgi configuration
################################################################################
# install my-git-lfs-fcgi SELinxu package
echo Installing my-git-lfs-fcgi SELinux package ...

cat << __EOF > /tmp/my-git-lfs-fcgi.te
module my-git-lfs-fcgi 1.0.0;
require {
  type httpd_t;
  type var_lib_t;
  type unconfined_service_t;
  class sock_file write;
  class unix_stream_socket connectto;
}
#============= httpd_t ==============
allow httpd_t var_lib_t:sock_file write;
allow httpd_t unconfined_service_t:unix_stream_socket connectto;
__EOF

checkmodule -m -o /tmp/my-git-lfs-fcgi.mod /tmp/my-git-lfs-fcgi.te
semodule_package -o /tmp/my-git-lfs-fcgi.pp -m /tmp/my-git-lfs-fcgi.mod
semodule -i /tmp/my-git-lfs-fcgi.pp

rm -f /tmp/my-git-lfs-fcgi.te /tmp/my-git-lfs-fcgi.mod /tmp/my-git-lfs-fcgi.pp

# remove SetEnvIf directive from /etc/httpd/conf.d/git-lfs-fcgi.conf
sed -e 's/\(^[ \t]*SetEnvIf Authorization .*$\)/#\1/g' \
    -i /etc/httpd/conf.d/git-lfs-fcgi.conf

# configure /etc/git-lfs-fcgi/git-lfs-fcgi.conf
if [ ! _ = _${__HOSTNAME} ]; then
  echo Configuring /etc/git-lfs-fcgi/git-lfs-fcgi.conf ...
  sed -e "s/^base_url .*$/base_url \"http:\/\/${__HOSTNAME}\"/g" \
      -i /etc/git-lfs-fcgi/git-lfs-fcgi.conf
fi

# create htpasswd file
echo Creating /etc/httpd/conf/htpasswd.git ...
touch /etc/httpd/conf/htpasswd.git
htpasswd -bB /etc/httpd/conf/htpasswd.git gituser example
echo "Git repository user gituser (password example) registerd."

# enable services
echo Enabling httpd and git-lfs-fcgi services ...
systemctl enable --now httpd git-lfs-fcgi

# show complete message
echo git-lfs-fcgi installation complete.
echo -e "Please set user and passwod using following command ...\n\
    htpasswd -bB /etc/httpd/conf/htpasswd.git <user> <passwd>"
