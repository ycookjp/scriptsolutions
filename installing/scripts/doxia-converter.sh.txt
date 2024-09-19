#!/bin/sh
proxy_url=
################################################################################
# Doxia Converter Tool Wrapper
# Usage: doxia-converter.sh <input-file>
#
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

if [ x$PROXY_URL != x ]; then
  __curlxopt="-x $PROXY_URL"
fi
__inputdir=$(dirname $0)
__doxiajar=${__inputdir}/doxia-converter-1.3-jar-with-dependencies.jar

if [ $# -eq 0 ]; then
  echo Usage `basename $0` \<input-file\>
  exit
fi

__inputfile=$1
__inputsuffix=${__inputfile##*.}
__inputfmt=$(if [ x$__inputsuffix == xmd ]; then echo markdown; else echo $__inputsuffix; fi)
__infmtopt=
for __opt in apt confluence docbook fml markdown twiki xdoc xhtml xhtml5 autodetect; do
  if [ x$__inputfmt == x$__opt ]; then
    __infmtopt="-from $__opt"
  fi
done
__outputfile=$(basename $__inputfile .$__inputsuffix).html

echo "java -jar $__doxiajar -in $__inputfile $__infmtopt -out . -to xhtml5"
java -jar $__doxiajar -in $__inputfile $__infmtopt -out . -to xhtml5
__exitcode=$?
if [ $__exitcode != 0 ]; then
  echo Error: Fail to convert $__inputfile
  exit 1
fi
nkf --numchar-input ./$(basename $__inputfile).xhtml5 | tee ./$__outputfile
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

