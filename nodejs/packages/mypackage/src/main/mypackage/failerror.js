/**
 * @file failerror.js - システムエラーが発生する関数の実装。
 * @copyright ycook
 *   [homepage] https://github.com/ycookjp/
 */

/**
 * 開始、終了インデックスを指定して部分文字列を取得します。
 * @param str {String} 入力文字列
 * @param beginIndex {int} 部分文字列の開始インデックスを指定します。
 *     部分文字列はこのインデックスから開始します。
 * @param endIndex {int} 部分文字列の終了インデックスを指定します。部分文字列は
 *     このインデックスの１つ前の文字で終了します。このパラメータを省略した
 *     場合は、部分文字列は開始インデックスから文字列の最後までになります。
 * @returns {String} 取得した部分文字列を返します。
 */
function substring(str, beginIndex, endIndex=str.length) {
	var ret = '';

    for (i = beginIndex; i <= endIndex; i++) {
        ret = ret + str[i];
    }

	return ret;
}

exports.substring = substring;
