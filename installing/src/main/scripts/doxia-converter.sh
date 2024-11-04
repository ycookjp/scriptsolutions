#!/bin/sh
proxy_url=
################################################################################
# Doxia Converter Tool Wrapper
# Usage: doxia-converter.sh <options> <input-file>
# Options
#   * --inEncoding=<encoding>: Inut file encoding (default: UTF-8)
#   * --outEncoding=<encoding> : Output file encoding (default: UTF-8)
#   * --from=<format>: Input format
#   * --noLinenum: No line number in the code block
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
__from=
__noLinenum=
while [ $# -gt 0 ]; do
  case $1 in
  --*)
    __optName=${1%%=*}
    __optValue=${1#*=}
    # if options's value is not specified, value shuld be '1'
    if [ x$__optName == x$__optValue ]; then
      __optValue=1
    fi
    __optName=${__optName/--/__}
    echo "${__optName}=${__optValue}"
    eval "${__optName}=${__optValue}"
    shift
    ;;
  -h)
    echo "__help=1"
    __help=1
    shift
    ;;
  -*)
    shift
    ;;
  *)
    break
    ;;
  esac
done

if [ x$proxy_url != x ]; then
  __curlxopt="-x $proxy_url"
fi
__commanddir=$(dirname $0)
__doxiajar=${__commanddir}/doxia-converter-1.3-jar-with-dependencies.jar

if [ $# -eq 0 -o x$__help != x ]; then
  echo "Usage $(basename $0) <options> <input-file>"
  echo "Options:"
  echo "  * --inEncoding=<encoding>: Input file encoding."
  echo "  * --outencoding=<encoding>: Output file encoding."
  echo "  * --from=<format>: Input format."
  echo "  * --noLinenum: No line number in the code block" 
  echo "  Supported encoding: UTF-8, Shift_JIS, ISO-2022-JP, EUC-JP"
  exit
fi

# input file format
__inputfile=$1
__inputsuffix=${__inputfile##*.}
__inputfmt=$(if [ x$__inputsuffix == xmd ]; then echo markdown; else echo $__inputsuffix; fi)
if [ x$__from == x ]; then
  for __opt in apt confluence docbook fml markdown twiki xdoc xhtml xhtml5 autodetect; do
    if [ x$__inputfmt == x$__opt ]; then
      __from=$__opt
    fi
  done
fi
if [ x$__from == x ]; then
  __from=apt
fi

# output file
__outputfile=$(basename $__inputfile .$__inputsuffix).html

# doxia-converter/nkf options
__doxiaOptions="-from $__from"
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

echo "$__javaCommand -jar $__doxiajar $__doxiaOptions -in $__inputfile -out . -to xhtml5"
$__javaCommand -jar $__doxiajar $__doxiaOptions -in $__inputfile -out . -to xhtml5
__exitcode=$?
if [ $__exitcode != 0 ]; then
  echo Error: Fail to convert $__inputfile
  if [ -f ./$(basename $__inputfile).xhtml5 ]; then
    rm -f ./$(basename $__inputfile).xhtml5
  fi
  exit 1
fi
echo "nkf $__nkfOption --numchar-input ./$(basename $__inputfile).xhtml5 | tee ./$__outputfile"
nkf $__nkfOption --numchar-input ./$(basename $__inputfile).xhtml5 | tee ./$__outputfile
rm -f ./$(basename $__inputfile).xhtml5

### Apply skin ###
sed -e 's/<meta /\n<meta /g' -e 's/<\/head>/\n<\/head>/g' -e 's/<body>/\n<body>/g' -i ./$__outputfile
if [ x$__noLinenum == x ]; then
  sed -e '/<div class="source">[ \t]*$/N;s/\(<div class="source">[ \t\n]*<pre[^>]*\)>/\1 class="prettyprint linenums">/g' -i ./$__outputfile
fi

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
