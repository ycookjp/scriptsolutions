index = require('../index');

/**
 * stringutil.findStringRepeat 関数のテストを実施します。
 */
function index_calculateWinner_test() {
    // Pattern-1
    // O O O
    // X
    // X
    squares = ['O', 'O', 'O', 'X', null, null, 'X', null, null];
    result = index.calculateWinner(squares);
    expect(result).toEqual('O');

    // Pattern-2
    // O X X
    // O 
    // O
    squares = ['O', 'X', 'X', 'O', null, null, 'O', null, null];
    result = index.calculateWinner(squares);
    expect(result).toEqual('O');

    // Pattern-3
    // O X X
    //   O
    //     O
    squares = ['O', 'X', 'X', null, 'O', null, null, null, 'O'];
    result = index.calculateWinner(squares);
    expect(result).toEqual('O');
}
