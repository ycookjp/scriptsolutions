#!/bin/sh
proxy_url=
################################################################################
# Doxia Converter Tool Wrapper
# Usage: doxia-converter.sh <options> <input-file>
# Options
#   * --inEncoding: Inut file encoding (default: UTF-8)
#   * --outEncoding : Output file encoding (default: UTF-8)
#   Supported encoding: UTF-8, Shift_JIS, ISO-2022-JP, EUC-JP
# Description
#   Convert <input-file> to xtml5 format. Output file name is "base name of
#   <input-file>" + ".html".
# Requirements
# * java command
#   Install java-<version>-openjdk-headless package.
# * doxia-converter-1.3-jar-with-dependencies.jar
#   Download it from follwing url and place it to this directory.
#   * https://repo.maven.apache.org/maven2/org/apache/maven/doxia/doxia-converter/1.3/
# * nkf command
#   Install nkf package.
#   For Windows, download nkfwin.zip from
#   http://www.vector.co.jp/soft/dl/win95/util/se295331.html
#   and unzip it. Rename following exe file to nkf.exe.
#   * vc2005/win32(98,Me,NT,2000,XP,Vista,7)Windows-31J/nkf32.exe
#
# Settings
# * Proxy setting
#   Set proxy_url environment value to proxy url.
################################################################################

# options
__inEncoding=UTF-8
__outEncoding=UTF-8
for p in $*; do
  if [ ${1:0:2} == -- ]; then
    __optName=${1%%=*}
    __optName=${__optName/--/__}
    __optValue=${1#*=}
    eval "${__optName}=${__optValue}"
    shift
  fi
done

if [ x$proxy_url != x ]; then
  __curlxopt="-x $proxy_url"
fi
__inputdir=$(dirname $0)
__doxiajar=${__inputdir}/doxia-converter-1.3-jar-with-dependencies.jar

if [ $# -eq 0 ]; then
  echo "Usage $(basename $0) <options> <input-file>"
  echo "Options:"
  echo "  * --inEncoding: Input file encoding."
  echo "  * --outencoding: Output file encoding."
  echo "  Supported encoding: UTF-8, Shift_JIS, ISO-2022-JP, EUC-JP"
  exit
fi

# input file format
__inputfile=$1
__inputsuffix=${__inputfile##*.}
__inputfmt=$(if [ x$__inputsuffix == xmd ]; then echo markdown; else echo $__inputsuffix; fi)
__infmtopt=
for __opt in apt confluence docbook fml markdown twiki xdoc xhtml xhtml5 autodetect; do
  if [ x$__inputfmt == x$__opt ]; then
    __infmtopt="-from $__opt"
  fi
done

# output file
__outputfile=$(basename $__inputfile .$__inputsuffix).html

# doxia-converter/nkf options
__doxiaOptions=
__nkfOption=
if [ x$__inEncoding != x ]; then
  __doxiaOptions="$__doxiaOptions -inEncoding $__inEncoding"
fi
if [ x$__outEncoding != x ]; then
  __doxiaOptions="$__doxiaOptions -outEncoding $__outEncoding"
  case $__outEncoding in
    UTF-8)
      __nkfOption="$__nkfOption -W -w"
      ;;
    Shift_JIS)
      __nkfOption="$__nkfOption -S -s"
      ;;
    ISO-2022-JP)
      __nkfOption="$__nkfOption -J -j"
      ;;
    EUC-JP)
      __nkfOption="$__nkfOption -E -e"
  esac
fi

# java command and options
__javaCommand=java
if [ "x$JAVA_HOME" != "x" ]; then
  __javaCommand="${JAVA_HOME}/bin/java"
fi
if [ "x$JAVA_OPTS" != "x" ]; then
  __javaCommand="$__javaCommand $JAVA_OPTS"
fi

echo "$__javaCommand -jar $__doxiajar $__doxiaOptions -in $__inputfile $__infmtopt -out . -to xhtml5"
$__javaCommand -jar $__doxiajar $__doxiaOptions -in $__inputfile $__infmtopt -out . -to xhtml5
__exitcode=$?
if [ $__exitcode != 0 ]; then
  echo Error: Fail to convert $__inputfile
  exit 1
fi
echo "nkf $__nkfOption --numchar-input ./$(basename $__inputfile).xhtml5 | tee ./$__outputfile"
nkf $__nkfOption --numchar-input ./$(basename $__inputfile).xhtml5 | tee ./$__outputfile
rm ./$(basename $__inputfile).xhtml5

### Apply skin ###
sed -e 's/<meta /\n<meta /g' -e 's/<\/head>/\n<\/head>/g' -e 's/<body>/\n<body>/g' -e 's/<pre>/<pre class="prettyprint linenums">/g' -i ./$__outputfile

sed 's/\(^<meta charset=.*\/>$\)/<meta name="viewport" content="width=device-width, initial-scale=1" \/>\n\1\n<link rel="shortcut icon" href="images\/favicon.ico"\/>\n<link rel="stylesheet" href=".\/css\/apache-maven-fluido-2.0.0-M6.min.css" \/>\n<link rel="stylesheet" href=".\/css\/site.css" \/>\n<link rel="stylesheet" href=".\/css\/print.css" media="print" \/>\n<script src=".\/js\/apache-maven-fluido-2.0.0-M6.min.js"><\/script>/g' -i ./$__outputfile

### Download css and js
if [ ! -d ./css ]; then mkdir -p ./css; fi
if [ ! -f ./css/apache-maven-fluido-2.0.0-M6.min.css ]; then
  curl $__curlxopt -LO --output-dir ./css https://maven.apache.org/css/apache-maven-fluido-2.0.0-M6.min.css
fi
if [ ! -f ./css/site.css ]; then
  curl $__curlxopt -LO --output-dir ./css https://maven.apache.org/css/site.css
fi
if [ ! -f ./css/print.css ]; then
  curl $__curlxopt -LO --output-dir ./css https://maven.apache.org/css/print.css
fi

if [ ! -d ./js ]; then mkdir -p ./js; fi
if [ ! -f ./js/apache-maven-fluido-2.0.0-M6.min.js ]; then
  curl $__curlxopt -LO --output-dir ./js https://maven.apache.org/js/apache-maven-fluido-2.0.0-M6.min.js
fi

