#! /bin/sh

# Eclipse command to download update site archive.
ECLIPSE_COMMAND=/opt/eclipse/eclipse

# Download interval. Ex. 1, 2s, 3m, 4h
DL_INTERVAL=1s

# Proxy URL
PROXY_URL=

################################################################################

if [ "x${PROXY_URL}" != "x" ]; then
  CURL_OPTS="-x ${PROXY_URL}"
  ECLIPSE_COMMAND="env http_proxy=${PROXY_URL} https_proxy=${PROXY_URL} ${ECLIPSE_COMMAND}"
fi

__archive_updatesite () {
  ##############################################################################
  # Usage : __archive_updatesite -o file-path url
  # Options :
  #   -o file-path : Specifies file path archived downloaded update site files.
  #   url
  ##############################################################################
  __OUTPUT_FILE__=

  # parse options
  for OPT in "$@"
  do
    case $OPT in
    -o)
      __OUTPUT_FILE__=$2
      shift 2
      ;;
    esac
  done
  shift $(($OPTIND - 1))

  __URL__=$1
  __TEMP_DIR__=/tmp/dropins-archive-$$

  if [ "x" = "x${__OUTPUT_FILE__}" -o "x" = "x${__URL__}" ]; then
    echo "Usage : __archive_updatesite -o file-path url"
    return -1
  fi

  if [ "/" != "`echo ${__OUTPUT_FILE__} | cut -c -1`" ]; then
    __OUTPUT_FILE__="`pwd`/${__OUTPUT_FILE__}"
  fi

  mkdir -p "`dirname ${__OUTPUT_FILE__}`"
  mkdir -p "${__TEMP_DIR__}"
  ${ECLIPSE_COMMAND} -verbose \
    -application org.eclipse.equinox.p2.artifact.repository.mirrorApplication \
    -source "${__URL__}" -destination "${__TEMP_DIR__}"
  (
    cd "${__TEMP_DIR__}"
    zip -r "${__OUTPUT_FILE__}" *
  )
  if [ -d "${__TEMP_DIR__}" ]; then
    rm -rf "${__TEMP_DIR__}"
  fi
}

__unzipfile () {
  ##############################################################################
  # Usage : __unzipfile [-x remove-pattern [remove-pattern ...]] \
  #         [-m pattern [pattern ...]] {-f file-name | -u url} output-path
  # Options :
  #   -x remove-pattern : When unzip downloaded file, deletes files which
  #       maches <remove-pattern> .
  #   -m pattern : When unzip downloaded file, deletes files which
  #       does not mach <pattern> .
  #   -f file-path : Specifies zip file path to be extracted .
  #   -u url : Specifies url to download . Download file will be placed at
  #       <file-path> . If -f option is ommitted, Download file will be placed
  #       at current directory .
  #   output-path : Unzips downloaded file to <output-path>
  ##############################################################################
  # initialize environment values
  __FILE_PATH__=
  __REMOVE_PATTERN__=
  __PATTERN__=
  __URL__=

  # parse options
  for OPT in "$@"
  do
    case $OPT in
    -x)
      __REMOVE_PATTERN__=$2
      shift 2
      ;;
    -m)
      __PATTERN__=$2
      shift 2
      ;;
    -f)
      __FILE_PATH__=$2
      shift 2
      ;;
    -u)
      __URL__=$2
      shift 2
      ;;
    esac
  done
  shift $(($OPTIND - 1))

  __OUTPUT_PATH__=$1

  if [ "x${__OUTPUT_PATH__}" = "x" -o  "x${__FILE_PATH__}" = "x" -a "x${__URL__}" = "x" ]; then
    echo "Usage : __unzipfile [-x remove-pattern [remove-pattern ...]]" 
    echo "       [-m pattern [pattern ...]] {-f file-name | -u url} output-path"
    return -1
  fi

  if [ "x${__FILE_PATH__}" = "x" ]; then
    __FILE_PATH__="`pwd`/`basename ${__URL__}`"
  fi

  __CURL_OPTS__=
  if [ "x${PROXY_URL}" != "x" ]; then
    __CURL_OPTS__="-x ${PROXY_URL}"
  fi

  # download file
  if [ "x" != "x${__URL__}" ]; then
    curl ${__CURL_OPTS__} -v -L --create-dirs -o "${__FILE_PATH__}" "${__URL__}"
    if [ x != x${DL_INTERVAL} ]; then
      sleep ${DL_INTERVAL};
    fi
  fi

  # unzip downloaded file
  __ECLIPSEDIR__=
  if [ -f "${__FILE_PATH__}" ]; then
    mkdir -p "${__OUTPUT_PATH__}"
    unzip -d "${__OUTPUT_PATH__}" "${__FILE_PATH__}"
    __PLUGINSDIR__="`find \"${__OUTPUT_PATH__}\" -type d -name 'plugins'`"
    if [ "x${__PLUGINSDIR__}" != "x" ]; then
      __ECLIPSEDIR__=`dirname "${__PLUGINSDIR__}"`
    fi
    if [ "x${__ECLIPSEDIR__}" != "x" ]; then
      for f in `ls -d ${__ECLIPSEDIR__}/* | grep -v features | grep -v plugins`; do
        rm -rf "$f"
      done
    fi
  fi

  # remove file(s)
  for d in ${__ECLIPSEDIR__}/features ${__ECLIPSEDIR__}/plugins; do
    if [ -d $d ]; then
    (
      cd $d
      if [ "x${__REMOVE_PATTERN__}" != "x" ]; then
        rm -rf ${__REMOVE_PATTERN__}
      fi
      if [ "x${__PATTERN__}" != "x" ]; then
        for f in `ls -I "${__PATTERN__}"`; do
          rm -rf $f
        done
      fi
    )
    fi
  done
}


ECLIPSE_URL_BASE=https://ftp.yz.yamagata-u.ac.jp/pub/eclipse

################################################################################
# Eclipse Papyrus
################################################################################
## Eclipse EMF
## requires for installing Eclipse Papyrus
#URL=https://download.eclipse.org/modeling/emf/emf/builds/release/2.30/
#PACKAGE_NAME=org.eclipse.emf_2.30
#FILE_NAME=${PACKAGE_NAME}.zip
## download archived site
#__archive_updatesite -o dropins-archive/${FILE_NAME} \
#  "${URL}"
## deploy plugin files
#__unzipfile -f "dropins-archive/${FILE_NAME}" \
#  -x '*.doc_* *.source_*' \
#  dropins/${PACKAGE_NAME}/eclipse

# Eclipse Common Build Infrastructure
URL=https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/cbi/tpd/3.0.0-SNAPSHOT/org.eclipse.cbi.targetplatform-3.0.0.202005061025.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse EMF Transaction
URL=https://download.eclipse.org/modeling/emf/transaction/updates/releases/R201805140824
PACKAGE_NAME=org.eclipse.emf.transaction_1.12.0
FILE_NAME=${PACKAGE_NAME}.zip
# download archived site
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.optional.* *.doc_* *.examples_* *.source_* *.tests_*' \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse EMF Validation
URL=https://download.eclipse.org/modeling/emf/validation/updates/releases/R202008210805
PACKAGE_NAME=org.eclipse.emf.validation_1.12.2
FILE_NAME=${PACKAGE_NAME}.zip
# download archived site
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.optional.* *.doc_* *.examples_* *.source_* *.tests_*' \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse Modeling Workflow Engine
URL=${ECLIPSE_URL_BASE}/modeling/emft/mwe/downloads/drops/2.13.0/R202205191115/emft-mwe-2-lang-Update-2.13.0.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.source_*' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse GMF Runtime
# requires for installing Eclipse Papyrus
URL=https://download.eclipse.org/modeling/gmp/gmf-runtime/updates/releases/R202204130739
PACKAGE_NAME=org.eclipse.gmf.runtime_1.7.0.202204130739
FILE_NAME=${PACKAGE_NAME}.zip
# download archived site
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.examples_* *.source_* *.tests_*' \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse OCL
URL=${ECLIPSE_URL_BASE}/modeling/mdt/ocl/downloads/drops/6.17.1/R202203090840/mdt-ocl-Update-6.17.1.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.examples.* *.source_* *.sdk_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse QVT Operational
URL=${ECLIPSE_URL_BASE}/mmt/qvto/downloads/drops/3.10.7/R202206051149/mmt-qvto-Update-3.10.7.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.examples.* *.source_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse UML2
# requires for installing Eclipse Papyrus
URL=${ECLIPSE_URL_BASE}/modeling/mdt/uml2/downloads/drops/5.5.2/R202102281829/mdt-uml2-Update-5.5.2.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.examples.* *.source_* *.sdk_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse XTEXT
# requires for installing Eclipse Papyrus
URL=${ECLIPSE_URL_BASE}/modeling/tmf/xtext/downloads/drops/2.27.0/R202205300508/tmf-xtext-Update-2.27.0.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.examples.* *.source_* *.sdk_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse XWT
# requires for installing Eclipse Papyrus
URL=${ECLIPSE_URL_BASE}/xwt/release-1.4.100/xwt-archived-p2-site.zip
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.doc_* *.examples.* *.source_* *.sdk_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse

# Eclipse Papyrus
URL=https://download.eclipse.org/modeling/mdt/papyrus/updates/releases/2022-06
PACKAGE_NAME=org.eclipse.papyrus-6.2.0
FILE_NAME=${PACKAGE_NAME}.zip
# download archived site
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.sdk_* *.source_* *.gz' \
  dropins/${PACKAGE_NAME}/eclipse
