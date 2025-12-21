#! /bin/sh

################################################################################
# Script for downloading Eclipse plugins.
#
# To use this script on Windows, do following steps.
# 1. Download 64-bit Git for Windows Portable from https://git-scm.com and
#   unzip downloaded file.
# 2. Download zip-3.0-bin.zip and bzip2-1.0.5-bin.zip from
#   https://sourceforge.net/projects/gnuwin32/files/ .
# 3. Get bin/zip.exe from zip-3.0-bin.zip and bin/bzip2.dll
#   from bzip2-1.0.5-bin.zip, and copy them to PortableGit/mingw64/bin
#   directory.
# 4. Execute PortableGit/git-bash.exe to run Git Bash and run this script.
################################################################################
################################################################################
# This script downloads following Eclipse plugins.
#
#   [ ] aCute
#   [x] Amateras Modeler
#   [x] Asciidoctor Editor - AsciiDoc & PlantUML plugin
#   [x] Babel Language Packs
#   [x] Checkstyle
#   [x] Eclipse CDT - Eclipse C/C++ Development Tooling
#   [x] Eclipse Color Theme (with MoonRise UI Theme)
#   [x] Eclipse DLTK (used by Eclipse PDT)
#   [x] Eclipse PHP Development Tools
#   [ ] Emonic
#   [x] Enhanced Class Decompiler
#   [ ] ER Master
#   [x] JGit LFS
#   [x] Markdown Text Editor
#   [x] Nodeclipse
#   [x] PyDev for Eclipse
#   [x] SpotBugs
#   [ ] StatET
#   [x] StepCounter
#   [x] Subversive SVN Team Provider
#   [x] Subversive SVNKit
#   [x] Subversive SVN Connector
#   [ ] UMLet
#   [x] VisualVM Eclipse launcher
#   [x] WindowBuilder
################################################################################

# Eclipse command to download update site archiv
ECLIPSE_COMMAND=/opt/eclipse/eclipse

# Download interval. Ex. 1, 2s, 3m, 4h
DL_INTERVAL=1s

# Proxy URL
PROXY_URL=

# curl options
#CURL_OPTS="-k --http1.1"

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
  ${ECLIPSE_COMMAND} -verbose -nosplash \
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
  #         [-m "pattern [pattern ...]]" {-f file-name | -u url} output-path
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
    echo "       [-m \"pattern [pattern ...]]\" {-f file-name | -u url} output-path"
    return -1
  fi

  if [ "x${__FILE_PATH__}" = "x" ]; then
    __FILE_PATH__="`pwd`/`basename ${__URL__}`"
  fi

  __CURL_OPTS__=${CURL_OPTS}
  if [ "x${PROXY_URL}" != "x" ]; then
    __CURL_OPTS__="-x ${PROXY_URL} ${__CURL_OPTS__}"
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
        iflg=
        for p in ${__PATTERN__}; do
          iflg="$iflg -I $p"
        done
        for f in `ls $iflg`; do
          rm -rf $f
        done
      fi
    )
    fi
  done
}


ECLIPSE_URL_BASE=https://ftp.yz.yamagata-u.ac.jp/pub/eclipse
BABEL_URL_BASE="${ECLIPSE_URL_BASE}/technology/babel/babel_language_packs/R0.20.0RC4/2022-12"

# aCute
download_acute_plugin () {
  URL='https://download.eclipse.org/acute/snapshots/'
  PACKAGE_NAME=org.eclipse.acute_0.3.3.202504111135
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Amateras Modeler
download_amaterasmodeler_plugin() {
  URL='https://takezoe.github.io/amateras-update-site/'
  VERSION=2.3.0
  PACKAGE_NAME=net.java.amateras.modeler_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -m "*_${VERSION}.* jp.sf.amateras.htmleditor_*" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Asciidoctor Editor
# https://github.com/de-jcup/eclipse-asciidoctor-editor
download_asciidoctoreditor_plugin () {
  URL='https://de-jcup.github.io/update-site-eclipse-asciidoctor-editor/update-site/'
  VERSION=3.1.2
  PACKAGE_NAME=de.jcup.asciidoctoreditor_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Babel Language Packs
download_babel_plugin () {
  PACKAGE_NAME=BabelLanguagePack-R0.20.0RC4_v20230220105658
  URL_LIST="
  ${BABEL_URL_BASE}/BabelLanguagePack-datatools-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-eclipse-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.emf-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.graphiti-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.mdt.bpmn2-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-modeling.tmf.xtext-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-mylyn-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-rt.rap-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-soa.bpmn2-modeler-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.egit-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.handly-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.jgit-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.lsp4e-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.packaging-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.packaging.mpc-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.passage-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-technology.tm4e-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.cdt-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.gef-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.mat-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.tm-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-tools.tracecompass-ja_4.26.0.v20230220105658.zip
  ${BABEL_URL_BASE}/BabelLanguagePack-webtools-ja_4.26.0.v20230220105658.zip
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
  VERSION=12.0.1.202511131535
  URL="https://checkstyle.org/eclipse-cs-update-site/releases/${VERSION}"
  PACKAGE_NAME=net.sf.eclipsecs.checkstyle_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -x 'org.eclipse.* *.doc_* *.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Eclipse CDT
download_cdt_plugin () {
  URL="${ECLIPSE_URL_BASE}/tools/cdt/releases/12.3/cdt-12.3.0/cdt-12.3.0.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    -x '*.sdk_* *.source_* *.gz' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Eclipse Color Theme (with MoonRise UI Theme)
download_eclipse_color_theme_plugin () {
  URL=http://eclipse-color-theme.github.io/update
  PACKAGE_NAME=eclipse-color-theme_1.0.0
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archive site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
  # download MoonRise UI Theme
  URL=https://github.com/guari/eclipse-ui-theme/raw/refs/heads/master/com.github.eclipseuitheme.themes.plugin/bin/com.github.eclipseuitheme.moonrise_0.8.9.jar
  FILE_NAME=`basename "${URL}" | sed 's/?raw=true//g'`
  curl ${__CURL_OPTS__} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
  if [ x != x${DL_INTERVAL} ]; then
    sleep ${DL_INTERVAL};
  fi
  mkdir -p "dropins/${PACKAGE_NAME}/eclipse/plugins"
  cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/plugins"
}


# Eclipse DLTK (used by Eclipse PDT)
download_eclipse_dltk_plugin () {
  URL="https://download.eclipse.org/technology/dltk/updates-nightly/"
  PACKAGE_NAME=org.eclipse.dltk_6.4.2.202509021500
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -m 'org.eclipse.dltk.*' \
    -x '*.sdk_* *.source_* *.tests_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Eclipse PHP Development Tools
download_eclipse_pdt_plugin () {
  URL='https://download.eclipse.org/tools/pdt/updates/8.5/'
  PACKAGE_NAME=org.eclipse.php_8.5.0.202512041151
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -x '*.sdk_* *.source_* *.gz' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Emonic
download_emonic_plugin () {
  URL='https://sourceforge.net/projects/emonic/files/latest/download'
  PACKAGE_NAME=emonic_0.4.0
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Enhanced Class Decompiler
download_enanced_class_decompiler_plugin () {
  URL='https://github.com/ecd-plugin/ecd/releases/download/v3.5.1.20240613/com.github.ecd-plugin.update-3.5.1.zip'
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    -x '*.source_* *.source.*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# ER Master
download_ermaster_plugin() {
  URL='http://ermaster.sourceforge.net/update-site/'
  VERSION=1.0.0.v20150619-0219
  PACKAGE_NAME=org.insightech.er_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -m "*_${VERSION}.*" \
    dropins/${PACKAGE_NAME}/eclipse
}


# JGit LFS
download_jgit_plugin () {
  URL="${ECLIPSE_URL_BASE}/egit/updates-7.5/org.eclipse.egit.repository-7.5.0.202512021534-r.zip"
  PACKAGE_NAME=`basename "${URL}" .zip | sed 's/\.egit\./.jgit./g'`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    -x '*.source_* *.gz' \
    -m 'org.eclipse.jgit*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Markdown Text Editor
# https://www.winterwell.com/software/markdown-editor.php
# https://github.com/winterstein/Eclipse-Markdown-Editor-Plugin/releases
download_markdown_editor_plugin () {
  URL='https://nodeclipse.github.io/updates/markdown/'
  VERSION=1.2.0-201501260515
  PACKAGE_NAME=markdown.editor-${VERSION} 
  FILE_NAME=${PACKAGE_NAME}.zip
  # download archived site
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Nodeclipse
download_nodeclipse_plugin () {
  # https://nodeclipse.github.io/updates/
  URL='https://sourceforge.net/projects/nodeclipse/files/latest/download'
  VERSION=1.0.2-201509250223
  PACKAGE_NAME=org.nodeclipse-${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    -x "com.github.eclipsecolortheme* com.github.eclipseuitheme.themes.* winterwell.markdown_*" \
    dropins/${PACKAGE_NAME}/eclipse
}


# PyDev for Eclipse
download_pydev_plugin () {
  URL='https://www.pydev.org/update_sites/13.1.0'
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
  URL='https://spotbugs.github.io/eclipse/'
  PACKAGE_NAME=com.github.spotbugs.plugin.eclipse_4.9.8.r202510181643-c1fa7f2
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    dropins/${PACKAGE_NAME}/eclipse
}


# StatET
download_statet_plugin () {
  URL="${ECLIPSE_URL_BASE}/statet/releases/4.11.0/statet-repository-E202506-incubation-4.11.0-202506120600-r.zip"
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f dropins-archive/${FILE_NAME} -u "${URL}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# StepCounter
download_stepcounter_plugin () {
  URL='https://github.com/takezoe/stepcounter/releases/download/3.0.4/jp.sf.amateras.stepcounter_3.0.4.201805262142.jar'
  PACKAGE_NAME="`basename "${URL}" .jar`"
  FILE_NAME=`basename "${URL}"`
  curl ${__CURL_OPTS__} -v -L --create-dirs -o dropins-archive/${FILE_NAME} "${URL}"
  if [ x != x${DL_INTERVAL} ]; then
    sleep ${DL_INTERVAL};
  fi

  mkdir -p "dropins/${PACKAGE_NAME}/eclipse/plugins"
  cp "dropins-archive/${FILE_NAME}" "dropins/${PACKAGE_NAME}/eclipse/plugins"
}


# Subversive SVN Team Provider
# https://projects.eclipse.org/projects/technology.subversive
download_subversive_plugin () {
  URL='https://download.eclipse.org/technology/subversive/updates/release/5.1.0/'
  VERSION=5.1.0
  PACKAGE_NAME="org.eclipse.team.svn_${VERSION}"
  FILE_NAME="${PACKAGE_NAME}.zip"
  __archive_updatesite -o dropins-archive/${FILE_NAME} \
    "${URL}"
  # deploy plugin files
  __unzipfile -f dropins-archive/${FILE_NAME} \
    -x '*.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Subversive SVNKit
# https://svnkit.com/ # SVNKit Only
download_svnkit_plugin () {
  URL='http://eclipse.svnkit.com/1.10.x'
  VERSION=1.10.13
  PACKAGE_NAME=org.tmatesoft.svnkit_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o "dropins-archive/${FILE_NAME}" \
    "${URL}"
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    dropins/${PACKAGE_NAME}/eclipse
}


# Subversive SVN Connector
# https://github.com/arsysop/svn # SVN Connector only
download_svn_connector_plugin () {
  URL='https://arsysop.github.io/svn/release/'
  VERSION=1.0.1
  PACKAGE_NAME=ru.arsysop.svn.connectors.svnkit1_10_${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o "dropins-archive/${FILE_NAME}" \
    "${URL}"
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -m 'ru.arsysop.svn.connector* org.antlr.runtime* org.tmatesoft.*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# UMLet
download_umlet_plugin () {
  URL='https://www.umlet.com/download/umlet_15_1/umlet-eclipse-p2-15.1.zip'
  PACKAGE_NAME=`basename "${URL}" .zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f "dropins-archive/${FILE_NAME}" -u "${URL}" \
    dropins/${PACKAGE_NAME}
  mv dropins/${PACKAGE_NAME}/repository dropins/${PACKAGE_NAME}/eclipse
}


# VisualVM Eclipse launcher
download_visualvm_plugin () {
  URL='https://github.com/oracle/visualvm/releases/download/2.1.2/visualvm_launcher_u3_eclipse_sig.zip'
  PACKAGE_NAME=`basename "${URL}" _sig.zip`
  FILE_NAME=`basename "${URL}"`
  __unzipfile -f dropins-archive/${FILE_NAME} -u "${URL}" \
    dropins/${PACKAGE_NAME}
  mv dropins/${PACKAGE_NAME}/${PACKAGE_NAME} dropins/${PACKAGE_NAME}/eclipse
}


# WindowBuilder
download_windowsbuilder_plugin () {
  URL='https://download.eclipse.org/windowbuilder/updates/release/1.22.0'
  VERSION=1.22.0
  PACKAGE_NAME=WindowBuilder-${VERSION}
  FILE_NAME=${PACKAGE_NAME}.zip
  __archive_updatesite -o "dropins-archive/${FILE_NAME}" \
    "${URL}"
  __unzipfile -f "dropins-archive/${FILE_NAME}" \
    -m 'org.eclipse.wb.* com.evolvedbinary.thirdparty.* com.jgoodies.* com.miglayout.* com.sun.xml.bind.jaxb-osgi_* io.github.toolfactory.* javax.xml_* net.bytebuddy.byte-buddy_* org.apache.commons.logging_* org.burningwave.* org.mvel2_*' \
    -x '*.doc_* *.source_*' \
    dropins/${PACKAGE_NAME}/eclipse
}


# Download eclipse plugins
## aCute: org.eclipse.acute_x.x.x.yyyyMMDDHHMM
#download_acute_plugin
# Amateras Modeler: net.java.amateras.modeler_x.x.x
download_amaterasmodeler_plugin
# Asciidoctor Editor: de.jcup.asciidoctoreditor_x.x.x
download_asciidoctoreditor_plugin
# Babel Language Packs: BabelLanguagePack-Rx.x.x-ja_vYYYYMMDDHHMMSS
download_babel_plugin
# Checkstyle: net.sf.eclipsecs.checkstyle_x.x.x.YYYYMMDDHHMM
download_checkstyle_plugin
# Eclipse CDT: cdt-x.x.x
download_cdt_plugin
# Eclipse Color Theme: eclipse-color-theme_x.x.x
download_eclipse_color_theme_plugin
# Eclipse DLTK: =org.eclipse.dltk_6.4.2.YYYYMMDDHHMM
download_eclipse_dltk_plugin
# Eclipse PHP Development Tools: org.eclipse.php_x.x.x.YYYYMMDDHHMM
download_eclipse_pdt_plugin
## Emonic: emonic_x.x.x
#download_emonic_plugin
# Enhanced Class Decompiler:com.github.ecd-plugin.update-x.x.x
download_enanced_class_decompiler_plugin
## ER Master: org.insightech.er_x.x.x.vYYYYMMDD-HHMM
#download_ermaster_plugin
# JGit LFS: org.eclipse.jgit.repository-x.x.x.YYYYMMDDHHMM-r
download_jgit_plugin
# Markdown Text Editor: markdown.editor-x.x.x-YYYYMMDDHHMM
download_markdown_editor_plugin
# Nodeclipse: org.nodeclipse-x.x.x-YYYYMMDDHHMM
download_nodeclipse_plugin
# PyDev for Eclipse: org.python.pydev_x.x.x
download_pydev_plugin
# SpotBugs: com.github.spotbugs.plugin.eclipse_x.x.x.rYYYYMMDDHHMM-xxxxxxx
download_spotbugs_plugin
## StatET: statet-repository-EYYYYMM-incubation-x.x.x-YYYYMMDDHHMM-r
#download_statet_plugin
# StepCounter: jp.sf.amateras.stepcounter_x.x.x.YYYYMMDDHHMM
download_stepcounter_plugin
# Subversive SVN Team Provider: org.eclipse.team.svn_x.x.x
download_subversive_plugin
# Subversive SVNKit: org.tmatesoft.svnkit_x.x.x
download_svnkit_plugin
# Subversive SVN Connector: ru.arsysop.svn.connector.svnkit1_10_x.x.x
download_svn_connector_plugin
## UMLet: umlet-eclipse-p2-x.x
#download_umlet_plugin
# VisualVM Eclipse launcher: visualvm_launcher_u3_eclipse
download_visualvm_plugin
# WindowBuilder: WindowBuilder-x.x.x
download_windowsbuilder_plugin


# file/directory permission
chmod -R a+r dropins
chmod a+x `find dropins -type d`
