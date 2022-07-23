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


# Amateras UML
URL='https://osdn.net/projects/amateras/downloads/56447/AmaterasUML_1.3.4.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f dropins-archive/${FILE_NAME} \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse/plugins
mv dropins/${PACKAGE_NAME}/eclipse/plugins/${PACKAGE_NAME}/*.jar dropins/${PACKAGE_NAME}/eclipse/plugins
rm -rf "dropins/${PACKAGE_NAME}/eclipse/plugins/${PACKAGE_NAME}"


# Babel
PACKAGE_NAME=BabelLanguagePack-ja_4.18.0.v20201226020001
URL_LIST="
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-datatools-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-eclipse-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-modeling.emf-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-modeling.mdt.bpmn2-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-modeling.tmf.xtext-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-mylyn-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-rt.rap-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-soa.bpmn2-modeler-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.egit-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.handly-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.jgit-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.lsp4e-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.packaging-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.packaging.mpc-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.passage-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-technology.tm4e-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-tools.cdt-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-tools.gef-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-tools.tracecompass-ja_4.19.0.v20210327020002.zip
https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/technology/babel/babel_language_packs/R0.18.3/2021-03/BabelLanguagePack-webtools-ja_4.19.0.v20210327020002.zip
"
for URL in $URL_LIST; do
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${PACKAGE_NAME}/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}
done


# Checkstyle
#URL='https://sourceforge.net/projects/eclipse-cs/files/Eclipse%20Checkstyle%20Plug-in/8.7.0/net.sf.eclipsecs-updatesite_8.7.0.201801131309.zip/download'
#PACKAGE_NAME=net.sf.eclipsecs-updatesite_8.7.0.201801131309
#FILE_NAME=${PACKAGE_NAME}.zip
#__unzipfile -f "dropins-archive/${FILE_NAME}" \
#    -x '*.source_*' \
#    -u "${URL}" \
#    dropins/${PACKAGE_NAME}/eclipse
# douload archive site
URL=https://checkstyle.org/eclipse-cs-update-site/
PACKAGE_NAME=net.sf.eclipsecs.ui_8.43.0
FILE_NAME=${PACKAGE_NAME}.zip
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f dropins-archive/${FILE_NAME} \
  -m '*_8.43.0.*' \
  -x '*.doc_* *.source_*' \
  dropins/${PACKAGE_NAME}/eclipse


# Eclipse CDT
URL='https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/tools/cdt/releases/10.3/cdt-10.3.0/cdt-10.3.0.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.sdk_* *.source_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# Eclipse PDT
URL='https://download.eclipse.org/tools/pdt/updates/7.2'
PACKAGE_NAME=org.eclipse.php_7.2.0.202005271851
FILE_NAME=${PACKAGE_NAME}.zip
# download archived site
__archive_updatesite -o dropins-archive/${FILE_NAME} \
  "${URL}"
# deploy plugin files
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.sdk_* *.source_* *.gz' \
  dropins/${PACKAGE_NAME}/eclipse


# Eclpse DLTK
URL='https://ftp.jaist.ac.jp/pub/eclipse/technology/dltk/downloads/drops/R6.2/R-6.2-202005020530/dltk-core-R-6.2-202005020530.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# Emonic
URL='https://sourceforge.net/projects/emonic/files/latest/download?source=directory'
PACKAGE_NAME=emonic_0.4.0
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# Enhanced Class Decompiler
URL='https://github.com/ecd-plugin/ecd/releases/download/3.1.1.201811062102/enhanced-class-decompiler-3.1.1.201811062102.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.source_* *.source.*' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# FindBugs
URL='https://sourceforge.net/projects/findbugs/files/findbugs%20eclipse%20plugin/3.0.1/edu.umd.cs.findbugs.plugin.eclipse_3.0.1.20150306-5afe4d1.zip/download'
PACKAGE_NAME=edu.umd.cs.findbugs.plugin.eclipse_3.0.1.20150306-5afe4d1
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse/plugins


# JGit LFS
URL='https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/egit/updates-5.11.1/org.eclipse.egit.repository-5.11.1.202105131744-r.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.source_* *.gz' \
  -m 'org.eclipse.jgit*' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# Nodeclipse
# https://nodeclipse.github.io/updates/
URL='https://sourceforge.net/projects/nodeclipse/files/latest/download'
PACKAGE_NAME=org.nodeclipse.site-1.0.2-201509250223
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# VisualVM Eclipse launcher
URL='https://github.com/oracle/visualvm/files/2724859/visualvm_launcher_u3_eclipse.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f dropins-archive/${FILE_NAME} \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}
mv dropins/${PACKAGE_NAME}/${PACKAGE_NAME} dropins/${PACKAGE_NAME}/eclipse


# Properties Editor
URL='https://ja.osdn.net/projects/propedit/downloads/68691/jp.gr.java_conf.ussiy.app.propedit_6.0.5.zip/'
PACKAGE_NAME=jp.gr.java_conf.ussiy.app.propedit_6.0.5
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f dropins-archive/${FILE_NAME} \
  -u  \
  dropins/${PACKAGE_NAME}


# PyDev
URL='https://sourceforge.net/projects/pydev/files/pydev/PyDev%208.3.0/PyDev%208.3.0.zip/download'
PACKAGE_NAME=PyDev_8.3.0
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f dropins-archive/${FILE_NAME} \
  -x '*.source_*' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# StatET
URL='https://download.eclipse.org/statet/integration/latest/statet-repository-E202106-incubation-4.4.0-202106190730.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f dropins-archive/${FILE_NAME} \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# StepCounter
URL='https://github.com/takezoe/stepcounter/releases/download/3.0.4/jp.sf.amateras.stepcounter_3.0.4.201805262142.jar'
PACKAGE_NAME="`basename "${URL}" .jar`"
FILE_NAME=`basename "${URL}"`
curl ${CURL_OPTS} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
if [ x != x${DL_INTERVAL} ]; then
  sleep ${DL_INTERVAL};
fi

mkdir -p "dropins/${PACKAGE_NAME}/eclipse/plugins"
cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/plugins"


# Subversive
URL='https://ftp.jaist.ac.jp/pub/eclipse/technology/subversive/4.0/builds/Subversive-4.0.5.I20170425-1700.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.sources_* *.gz' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# Subversive SVN Connector
URL='http://community.polarion.com/projects/subversive/download/eclipse/6.0/builds/Subversive-connectors-6.0.4.I20161211-1700.zip'
PACKAGE_NAME=`basename "${URL}" .zip`
FILE_NAME=`basename "${URL}"`
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -x '*.sources_*' \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse


# WindowBuilder Pro
URL='https://ftp.yz.yamagata-u.ac.jp/pub/eclipse/windowbuilder/1.9.7/repository.zip'
PACKAGE_NAME=WindowsBuilder_Pro-1.9.7
FILE_NAME=${PACKAGE_NAME}.zip
__unzipfile -f "dropins-archive/${FILE_NAME}" \
  -u "${URL}" \
  dropins/${PACKAGE_NAME}/eclipse
