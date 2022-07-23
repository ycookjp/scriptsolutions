/**
 * http://usejsdoc.org/
 */

failerror = require('../failerror');

/**
 * テストでエラーが発生する場合のテストを実施します。
 */
function failerror_substring_test() {
    expect(failerror.substring('hello world !', 0, 2)).toBe('he');
    expect(failerror.substring('hello world !', 5)).toBe('world !');
    expect(failerror.substring(null, 0, 1)).toBe(null);
}
test('failerror.substring test', failerror_substring_test);
