#!/bin/bash
################################################################################
# Name    : eclipse-updatesite-download.sh
# Usage   : eclipse-updatesite-download.sh artifact-name update-site-url
#           Download Eclipse update site and archive to zip file at current dir.
################################################################################

# parse option
while getopts hn: OPT
do
  case $OPT in
    h|*)
        echo "Download Eclipse update site and archive to zip file at current dir."
        echo "Usage: `basename $0` artifact-name update-site-url"
        exit
        ;;
  esac
done
shift $(($OPTIND - 1))

__ARTIFACT_NAME=$1
__UPDATE_URL=$2

if [ _${__ARTIFACT_NAME} = _ -o _${__UPDATE_URL} = _ ]; then
  echo "Download Eclipse update site and archive to zip file at current dir."
  echo "Usage: `basename $0` artifact-name update-site-url"
  exit
fi

which eclipse
if [ $? -gt 0 ]; then
  echo "You must set PATH to include eclipse command."
  exit
fi

__WORKDIR=${__ARTIFACT_NAME}${PPID}
__CURRENTDIR=`pwd`

eclipse -verbose \
  -application org.eclipse.equinox.p2.artifact.repository.mirrorApplication \
  -source ${__UPDATE_URL} \
  -destination ${__WORKDIR}

mkdir -p ${__WORKDIR}/${__ARTIFACT_NAME}/eclipse
mv -vi ${__WORKDIR}/features ${__WORKDIR}/${__ARTIFACT_NAME}/eclipse
mv -vi ${__WORKDIR}/plugins ${__WORKDIR}/${__ARTIFACT_NAME}/eclipse

(
  cd ${__WORKDIR}
  zip -r ${__CURRENTDIR}/${__ARTIFACT_NAME}.zip ${__ARTIFACT_NAME}
)

rm -rf ${__WORKDIR}
