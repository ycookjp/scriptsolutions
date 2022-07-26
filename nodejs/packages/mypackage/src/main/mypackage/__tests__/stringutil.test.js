stringutil = require('../stringutil');


/**
 * export されていない stringutil モジュールの findStringRepeat 関数の
 * テストを実施します。
 */
function test_stringutil_findStringRepeat() {
    // babel-plugin-rewire を使用して export されていない findStringRepeat
    // 関数を読み込む
    findStringRepeat = require('../stringutil').__get__('findStringRepeat');
    target="abbcccddddeeeee";
    // すべての範囲が対象
    expect(findStringRepeat(target, 'a')).toEqual([0, 1]);
    expect(findStringRepeat(target, 'b')).toEqual([1, 2]);
    expect(findStringRepeat(target, 'c')).toEqual([3, 3]);
    expect(findStringRepeat(target, 'd')).toEqual([6, 4]);
    expect(findStringRepeat(target, 'e')).toEqual([10, 5]);

    // 一致する範囲を開始、終了に設定
    expect(findStringRepeat(target, 'a', 0, 1)).toEqual([0, 1]);
    expect(findStringRepeat(target, 'b', 1, 3)).toEqual([1, 2]);
    expect(findStringRepeat(target, 'c', 3, 6)).toEqual([3, 3]);
    expect(findStringRepeat(target, 'd', 6, 10)).toEqual([6, 4]);
    expect(findStringRepeat(target, 'e', 10, 15)).toEqual([10, 5]);

    // 一致する範囲の開始位置＋1を設定
    expect(findStringRepeat(target, 'a', 1)).toEqual([-1, 0]);
    expect(findStringRepeat(target, 'b', 3)).toEqual([-1, 0]);
    expect(findStringRepeat(target, 'c', 7)).toEqual([-1, 0]);
    expect(findStringRepeat(target, 'd', 11)).toEqual([-1, 0]);
    expect(findStringRepeat(target, 'e', 16)).toEqual([-1, 0]);

    // 一致する一部分の範囲を開始、終了に設定
    expect(findStringRepeat(target, 'b', 2, 3)).toEqual([2, 1]);
    expect(findStringRepeat(target, 'c', 4, 6)).toEqual([4, 2]);
    expect(findStringRepeat(target, 'd', 7, 10)).toEqual([7, 3]);
    expect(findStringRepeat(target, 'e', 11, 15)).toEqual([11, 4]);
}
it('stringutil.findStringRepeat test', test_stringutil_findStringRepeat);

/**
 * stringutil.formatDateSimple 関数のテストを実施します。
 */
function test_stringutil_formatDateSimple() {
    date = new Date(1234, 5-1, 6, 12, 34, 56);
    expect(stringutil.formatDateSimple(date, 'yyyy')).toBe("1234");
    expect(stringutil.formatDateSimple(date, 'MM')).toBe("05");
    expect(stringutil.formatDateSimple(date, 'dd')).toBe("06");
    expect(stringutil.formatDateSimple(date, 'hh')).toBe("12");
    expect(stringutil.formatDateSimple(date, 'mm')).toBe("34");
    expect(stringutil.formatDateSimple(date, 'ss')).toBe("56");
}
it('stringutil.formatDateSimple test', test_stringutil_formatDateSimple);

/**
 * stringutil.formatDate 関数のテストを実施します。
 */
function test_stringutil_formatDate() {
	// 月日時分が１桁の場合
    date = new Date(234, 5-1, 6, 7, 8, 9);
    // yyyy-MM-dd hh:mm:ss
    expect(stringutil.formatDate(date, "yyyy-MM-dd hh:mm:ss")).toBe("0234-05-06 07:08:09");
    // yyyyMMddhhmmss
    expect(stringutil.formatDate(date, "yyyyMMddhhmmss")).toBe("02340506070809");
    // yy-M-d h:m:s
    expect(stringutil.formatDate(date, "yy-M-d h:m:s")).toBe("34-5-6 7:8:9");
    
    // 月日時分秒が２桁の場合
    date = new Date(2012, 10-1, 11, 12, 13, 14);
    // yyyy-MM-dd hh:mm:ss
    expect(stringutil.formatDate(date, "yyyy-MM-dd hh:mm:ss")).toBe("2012-10-11 12:13:14");
    // yyyyMMddhhmmss
    expect(stringutil.formatDate(date, "yyyyMMddhhmmss")).toBe("20121011121314");
    // yy-M-d h:m:s
    expect(stringutil.formatDate(date, "yy-M-d h:m:s")).toBe("12-10-11 12:13:14");
    // 書式文字列に年５桁、月日時分秒に３桁を指定した場合
    // yyyyy/MMM/ddd hhh:mmm:sss
    expect(stringutil.formatDate(date, "yyyyy/MMM/ddd hhh:mmm:sss")).toBe("02012/010/011 012:013:014");
    
    // 日本語a-zA-Z0-9YYYYDDHHSS => No match.
    expect(stringutil.formatDate(date, "日本語a-zA-Z0-9YYYYDDHHSS")).toBe("日本語a-zA-Z0-9YYYYDDHHSS");
}
it('stringutil.formatDate test', test_stringutil_formatDate);
