/**
 * @file stringutil.js - String utilities.
 * <br/>
 * @copyright ycookjp
 *   [homepage] https://github.com/ycookjp/
 */

/**
 * [No exported function]
 * 部分文字列が最初に出現した位置と連続する出現回数を取得します。
 * @param target {String} 部分文字列を探す対象の文字列を指定します。
 * @param sub {String} 出現を調べる部分文字列を指定します。
 * @param start {Numeric} 部分文字列の出現を調べる範囲の開始位置のインデックスを
 *         指定します。省略した時は、文字列の最初から出現を調べます。
 * @param end ｛Numeric} 部分文字列の出現を調べる範囲の終了位置（指定された
 *         インデックスの１つ前までを調べる）を指定します。
 * @returns {Array} 最初の養子に部分文字列が最初に出現した位置のインデックス、
 *         2番目の要素に出現回数を設定した配列を返します。
 */
function findStringRepeat(target, sub, start=0, end=-1) {
    if (end < 0) {
    	end = target.length;
    }
    var pos = target.indexOf(sub, start);
    var count = 0;

    if (pos >= 0 && pos < end) {
    	var nextPos = pos;
    	while (nextPos >= 0) {
    		count += 1;
    		nextPos = target.indexOf(sub, nextPos + sub.length);
    	}
    }

    return [pos, count];
}

/**
 * 日付けを書式文字列に従って文字列に変換する。
 * 
 * @param {Date} date Dateオブジェクト
 * @param {String} format 日付の書式文字列。
 *     書式文字列内に以下の文字列が含まれる場合は、その部分が日付けの年月日時
 *     分秒に置換される。
 *     <ul>
 *     <li>yyyy（西暦４桁）</li>
 *     <li>MM（月２桁、01-12）</li>
 *     <li>dd（日２桁、01-31）</li>
 *     <li>HH（時２桁、00-23）</li>
 *     <li>mm（分２桁、00-59）</li>
 *     <li>ss（秒２桁、00-19）</li>
 *     </ul>
 * @returns {String} 書式文字列に従って返還された日付の文字列
 */
function formatDateSimple(date, format) {
    var yearstr = ('0000' + date.getFullYear()).slice(-4);
    var monthstr = ('00' + (date.getMonth() + 1)).slice(-2);
    var datestr = ('00' + date.getDate()).slice(-2);
    var hoursstr = ('00' + date.getHours()).slice(-2);
    var munitesstr = ('00' + date.getMinutes()).slice(-2);
    var secondsstr = ('00' + date.getSeconds()).slice(-2);

    var formattedDate = format;

    formattedDate = formattedDate.replace('yyyy', yearstr);
    formattedDate = formattedDate.replace('MM', monthstr);
    formattedDate = formattedDate.replace('dd', datestr);
    formattedDate = formattedDate.replace('hh', hoursstr);
    formattedDate = formattedDate.replace('mm', munitesstr);
    formattedDate = formattedDate.replace('ss', secondsstr);

    return formattedDate;
}
/**
 * 書式文字列に従って datetime を文字列に変換します。
 * 書式文字列の変換規則は以下のとおりです。
 * 
 * <ul>
 * <li>
 *   書式文字列に'y', 'M', 'd', 'h', 'm', 's' の文字が含まれる場合、その部分を
 *   それぞれ date の年、月、時、分、秒に置換します。
 * </li>
 * <li>
 *   上記の文字が連続する場合は数値の桁を定義したことになります。連続する文字
 *   の個数よりも数値の桁が小さい場合は、数値の前に所定の桁数になるまで"0"を
 *   追加します。
 * </li>
 * <li>
 *   書式文字列が"7"の場合、数値（年）の桁数が書式文字列で設定された桁数より
 *   大きい場合は、書式文字列の桁数になるように数値の左側を切り捨てます。
 * </li>
 * 
 * @param {Date} date datetimeオブジェクト
 * @param {String} format 書式文字列
 * @returns {String} 書式文字列に従って変換された文字列を返します。
 */
function formatDate(date, format) {
    var converted = "";
    var start = 0;
    var end = format.length;

    while (start < end) {
        var c = format.charAt(start);
        if (c === "y" || c === "M" || c === "d" || c === "h" || c === "m"
                || c === "s") {
            var datechar = format.charAt(start);
            var found = findStringRepeat(format, datechar, start, end);
            var count = found[1];
                
            if (datechar === "y") {
                val = String(date.getFullYear());

                if (val.length > count) {
                    val = val.substring(val.length - count, val.length);
                }
            } else {
                if (datechar === "M") {
                    val = String(date.getMonth() + 1);
                } else if (datechar === "d") {
                    val = String(date.getDate());
                } else if (datechar === "h") {
                    val = String(date.getHours());
                } else if (datechar === "m") {
                    val = String(date.getMinutes());
                } else if (datechar === "s") {
                    val = String(date.getSeconds());
                }
            }

            if (val.length < count) {
                val = "0".repeat(count - val.length) + val;
            }
            converted = converted + val;
            start = start + count;
        } else {
            converted = converted + format.charAt(start);
            start += 1;
        }
    }
        
    return converted;
}

//exports.findStringRepeat = findStringRepeat;
exports.formatDateSimple = formatDateSimple;
exports.formatDate = formatDate;
