#! /bin/sh

# Eclipse command to download update site archive.
ECLIPSE_COMMAND=/opt/eclipse/eclipse

# Download interval. Ex. 1, 2s, 3m, 4h
DL_INTERVAL=1s

# Proxy URL
PROXY_URL=

# curl options
#CURL_OPTS="-k"

################################################################################

if [ "x${PROXY_URL}" != "x" ]; then
  CURL_OPTS="${CURL_OPTS} -x ${PROXY_URL}"
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
BABEL_URL_BASE="${ECLIPSE_URL_BASE}/technology/babel/babel_language_packs/R0.20.0RC1/2022-12"


# Babel
download_babel_plugin () {
  PACKAGE_NAME=BabelLanguagePack-R0.20.0RC1-ja_v20230110065230
  URL_LIST="
  ${BABEL_URL_BASE}/BabelLanguagePack-eclipse-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.emf-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.graphiti-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.mdt.bpmn2-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.tmf.xtext-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-rt.rap-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-soa.bpmn2-modeler-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.egit-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.jgit-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.lsp4e-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.packaging-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.packaging.mpc-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.passage-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.tm4e-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.cdt-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.gef-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.mat-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.tm-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.tracecompass-ja_.v20230110065230.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-webtools-ja_.v20230110065230.zip
  "
  for URL in $URL_LIST; do
    FILE_NAME=`basename "${URL}"`
    __unzipfile -f "dropins-archive/${PACKAGE_NAME}/${FILE_NAME}" \
      -u "${URL}" \
      dropins/${PACKAGE_NAME}
  done
}


# Checkstyle
download_checkstyle_plugin () {
  VERSION=10.4.0.202211151918
  #URL=https://checkstyle.org/eclipse-cs-update-site/
  URL=https://checkstyle.org/eclipse-cs-update-site/releases/${VERSION}
  PACKAGE_NAME=net.sf.eclipsecs.checkstyle_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -x '*.doc_* *.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
  # remove non target version
  for dirpath in dropins/${PACKAGE_NAME}/eclipse/features dropins/${PACKAGE_NAME}/eclipse/plugins; do
    mkdir ${dirpath}.bak
    mv ${dirpath}/*_${VERSION}.* ${dirpath}.bak
    rm -rf ${dirpath}
    mv ${dirpath}.bak ${dirpath}
  done
}


# Eclipse CDT
download_cdt_plugin () {
  URL="${ECLIPSE_URL_BASE}/tools/cdt/releases/11.0/cdt-11.0.0/cdt-11.0.0.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.sdk_* *.source_* *.gz' \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Eclipse PDT
download_pdt_plugin () {
  URL='https://download.eclipse.org/tools/pdt/updates/8.0'
  PACKAGE_NAME=org.eclipse.php_8.0.0.202112011911
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.sdk_* *.source_* *.gz' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Eclpse DLTK
download_dltk_plugin () {
  URL="${ECLIPSE_URL_BASE}/technology/dltk/downloads/drops/R6.2/R-6.2-202005020530/dltk-core-R-6.2-202005020530.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Emonic
download_emonic_plugin () {
  URL='https://sourceforge.net/projects/emonic/files/latest/download'
  PACKAGE_NAME=emonic_0.4.0
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Enhanced Class Decompiler
download_enanced_class_decompiler_plugin () {
  URL='https://github.com/ecd-plugin/ecd/releases/download/3.1.1.201811062102/enhanced-class-decompiler-3.1.1.201811062102.zip'
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.source_* *.source.*' \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# JGit LFS
download_jgit_plugin () {
  URL="${ECLIPSE_URL_BASE}/egit/updates-6.4/org.eclipse.egit.repository-6.4.0.202211300538-r.zip"
  PACKAGE_NAME=`basename "${URL}" .zip | sed 's/\.egit\./.jgit./g'`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.source_* *.gz' \
    -m 'org.eclipse.jgit*' \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Markdown Text Editor
download_markdown_editor_plugin () {
  # https://www.winterwell.com/software/markdown-editor.php
  PACKAGE_NAME=markdown.editor_0.2.3
  # features
  URL='https://www.winterwell.com/software/updatesite/features/markdown.editor.feature_0.2.3.jar'
  FILE_NAME=`basename "${URL}"`
  curl ${CURL_OPTS} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
  if [ x != x${DL_INTERVAL} ]; then
    sleep ${DL_INTERVAL};
  fi
  mkdir -p "dropins/${PACKAGE_NAME}/eclipse/features"
  cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/features"
  # plugins
  URL='https://www.winterwell.com/software/updatesite/plugins/winterwell.markdown_0.2.3.jar'
  FILE_NAME=`basename "${URL}"`
  curl ${CURL_OPTS} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
  if [ x != x${DL_INTERVAL} ]; then
    sleep ${DL_INTERVAL};
  fi
  mkdir -p "dropins/${PACKAGE_NAME}/eclipse/plugins"
  cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/plugins"
}


# Nodeclipse
download_nodeclipse_plugin () {
  # https://nodeclipse.github.io/updates/
  URL='https://sourceforge.net/projects/nodeclipse/files/latest/download'
  PACKAGE_NAME=org.nodeclipse.site-1.0.2-201509250223
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Properties Editor
download_properties_editor_plugin () {
  URL='https://ja.osdn.net/projects/propedit/downloads/68691/jp.gr.java_conf.ussiy.app.propedit_6.0.5.zip/'
  PACKAGE_NAME=jp.gr.java_conf.ussiy.app.propedit_6.0.5
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}
}


# PyDev
download_pydev_plugin () {
  URL='https://www.pydev.org/update_sites/10.1.1'
  PACKAGE_NAME=org.python.pydev_`basename "${URL}"`
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -x '*.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# SpotBugs
download_spotbugs_plugin () {
  URL=https://spotbugs.github.io/eclipse/
  PACKAGE_NAME=com.github.spotbugs.plugin.eclipse_4.7.3
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    dropins/${PACKAGE_NAME}/eclipse
}


# StatET
download_statet_plugin () {
  URL="${ECLIPSE_URL_BASE}/statet/releases/4.6.0/statet-repository-E202206-incubation-4.6.0-202209080600-r.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# StepCounter
download_stepcounter_plugin () {
  URL='https://github.com/takezoe/stepcounter/releases/download/3.0.4/jp.sf.amateras.stepcounter_3.0.4.201805262142.jar'
  PACKAGE_NAME="`basename "${URL}" .jar`"
  FILE_NAME=`basename "${URL}"`
  curl ${CURL_OPTS} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
  if [ x != x${DL_INTERVAL} ]; then
    sleep ${DL_INTERVAL};
  fi

  mkdir -p "dropins/${PACKAGE_NAME}/eclipse/plugins"
  cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/plugins"
}


# Subversive
download_subversive_plugin () {
  URL='https://download.eclipse.org/technology/subversive/4.8/release/latest/'
  PACKAGE_NAME='org.eclipse.team.svn_4.8.0.v20220904-1901'
  FILE_NAME="${PACKAGE_NAME}.zip"
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -x '*.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Subversive SVN Connector
download_svn_connector_plugin () {
  URL='https://osspit.org/eclipse/subversive-connectors/'
  PACKAGE_NAME=org.polarion.eclipse.team.svn.connector.svnkit1_10_6.1.0
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o "dropins-archive/${FILE_NAME}" \
    "${URL}"
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Mylyn
# Mylyn is required for installing UMLet
download_mylyn_plugin () {
  URL="${ECLIPSE_URL_BASE}/mylyn/drops/3.26.0/v20200731-0526/mylyn-3.26.0.v20200731-0526.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.source_* *.tests_*' \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# UMLet
download_umlet_plugin () {
  URL='https://www.umlet.com/download/umlet_15_0/umlet-eclipse-p2-15.0.0.zip'
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}
  mv dropins/${PACKAGE_NAME}/repository dropins/${PACKAGE_NAME}/eclipse
}


# VisualVM Eclipse launcher
download_visualvm_plugin () {
  URL='https://github.com/oracle/visualvm/releases/download/2.1.2/visualvm_launcher_u3_eclipse_sig.zip'
  PACKAGE_NAME=`basename "${URL}" _sig.zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}
  mv dropins/${PACKAGE_NAME}/${PACKAGE_NAME} dropins/${PACKAGE_NAME}/eclipse
}


# WindowBuilder Pro
download_windowsbuilder_plugin () {
  URL="${ECLIPSE_URL_BASE}/windowbuilder/1.11.0/repository.zip"
  PACKAGE_NAME=WindowBuilder_Pro-1.11.0
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Download eclipse plugins
# BabelLanguagePack-Rx.x.x-ja_vYYYYMMDDHHMMSS
download_babel_plugin
# net.sf.eclipsecs.checkstyle_x.x.x.YYYYMMDDHHMM
download_checkstyle_plugin
# cdt-x.x.x
download_cdt_plugin
# org.eclipse.php_x.x.x.YYYYMMDDHHMM
download_pdt_plugin
# dltk-core-R-x.x-YYYYMMDDHHMM
download_dltk_plugin
# emonic_x.x.x
download_emonic_plugin
# enhanced-class-decompiler-x.x.x.YYYYMMDDHHMM
download_enanced_class_decompiler_plugin
# org.eclipse.jgit.repository-x.x.x.YYYYMMDDHHMM-r
download_jgit_plugin
# markdown.editor_x.x.x
download_markdown_editor_plugin
# org.nodeclipse.site-x.x.x-YYYYMMDDHHMM
download_nodeclipse_plugin
# jp.gr.java_conf.ussiy.app.propedit_x.x.x
download_properties_editor_plugin
# org.python.pydev_x.x.x
download_pydev_plugin
# com.github.spotbugs.plugin.eclipse_x.x.x
download_spotbugs_plugin
# statet-repository-EYYYYMM-incubation-x.x.x-YYYYMMDDHHMM-r
download_statet_plugin
# jp.sf.amateras.stepcounter_x.x.x.YYYYMMDDHHMM
download_stepcounter_plugin
# org.eclipse.team.svn_x.x.x.vYYYYMMDD-HHMM
download_subversive_plugin
# org.polarion.eclipse.team.svn.connector.svnkitx_x_x.x.x
download_svn_connector_plugin
# mylyn-x.x.x.vYYYYMMDD-HHMM
download_mylyn_plugin
# umlet-eclipse-p2-x.x.x
download_umlet_plugin
# visualvm_launcher_u3_eclipse
download_visualvm_plugin
# WindowBuilder_Pro-x.x.x
download_windowsbuilder_plugin


# file/directory permission
chmod -R a+r dropins
chmod a+x `find dropins -type d`

################################################################################
# Amateras UML / Amateras Modeler
# Amateras UML dose'nt work recent Eclipse and not updated recently.
################################################################################
## Eclipse GMF Runtime
#URL='https://download.eclipse.org/modeling/gmp/gmf-runtime/updates/releases/R202204130739'
#PACKAGE_NAME=org.eclipse.gmf.runtime_1.7.0.202204130739
#FILE_NAME=${PACKAGE_NAME}.zip
## download archived site
#__archive_updatesite -o dropins-archive/${FILE_NAME} \
#  "${URL}"
## deploy plugin files
#__unzipfile -f "dropins-archive/${FILE_NAME}" \
#  -x '*.examples_* *.source_* *.tests_*' \
#  dropins/${PACKAGE_NAME}/eclipse

## Amateras UML
#URL='https://osdn.net/projects/amateras/downloads/56447/AmaterasUML_1.3.4.zip'
#PACKAGE_NAME=`basename "${URL}" .zip`
#FILE_NAME=`basename "${URL}"`
#__unzipfile -f dropins-archive/${FILE_NAME} \
#  -u "${URL}" \
#  dropins/${PACKAGE_NAME}/eclipse/plugins
#mv dropins/${PACKAGE_NAME}/eclipse/plugins/${PACKAGE_NAME}/*.jar dropins/${PACKAGE_NAME}/eclipse/plugins
#rm -rf "dropins/${PACKAGE_NAME}/eclipse/plugins/${PACKAGE_NAME}"

## Eclipse GEF
## GEF is required for installing Aamaters UML included Amateras Modeler.
#URL="${ECLIPSE_URL_BASE}/tools/gef/downloads/drops//5.3.8/R202206070201/GEF-Update-5.3.8.zip"
#PACKAGE_NAME=`basename "${URL}" .zip`
#FILE_NAME=`basename "${URL}"`
#__unzipfile -f "dropins-archive/${FILE_NAME}" \
#  -x '*.doc_* *.source_* *.gz' \
#  -u "${URL}" \
#  dropins/${PACKAGE_NAME}/eclipse

## Amateras Modeler
## homepage: https://github.com/takezoe/amateras-modeler
#URL='https://takezoe.github.io/amateras-update-site/'
#PACKAGE_NAME=AmaterasModelar-2.1.0
#FILE_NAME=${PACKAGE_NAME}.zip
## download archived site
#__archive_updatesite -o dropins-archive/${FILE_NAME} \
#  "${URL}"
## deploy plugin files
#__unzipfile -f "dropins-archive/${FILE_NAME}" \
#  -x '*.sdk_* *.source_* *.gz' \
#  dropins/${PACKAGE_NAME}/eclipse