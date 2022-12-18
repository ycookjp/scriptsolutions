const index = require('../index');
/**
 * stringutil.findStringRepeat 関数のテストを実施します。
 */
function test_calculateWinner() {
    const calculateWinner = index.__get__('calculateWinner');
    // Pattern-1
    // O O O
    // X
    // X
    var squares = ['O', 'O', 'O', 'X', null, null, 'X', null, null];
    let result = calculateWinner(squares);
    expect(result).toEqual('O');

    // Pattern-2
    // O X X
    // O 
    // O
    squares = ['O', 'X', 'X', 'O', null, null, 'O', null, null];
    result = calculateWinner(squares);
    expect(result).toEqual('O');

    // Pattern-3
    // O X X
    //   O
    //     O
    squares = ['O', 'X', 'X', null, 'O', null, null, null, 'O'];
    result = calculateWinner(squares);
    expect(result).toEqual('O');
}
it('calculateWinner test', test_calculateWinner);
