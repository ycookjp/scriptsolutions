/**
 * @file ３目並べゲームを作成するチュートリアル。
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

/**
 * Squareコンポーネントを描画する。
 * Squareコンポーネントの中に配置するbuttonタグを描画する。
 * buttonタグのonClick属性にはpropsのonClick関数を設定する。
 * @param props Squareコンポーネントのプロパティ。
 * @return tag buttonタグを返す。
 */
function Square(props) {
  return (
    <button className="square" onClick={props.onClick}>
      {props.value}
    </button>
  );
}

/**
 * Boardコンポーネント。
 */
class Board extends React.Component {
  /**
   * インデックスを指定してBoardコンポーネントの上に配置されるSquare
   * コンポーネントを描画する関数。
   * <ul>
   * <li>
   *   value属性 - Boardコンポーネントのプロパティのsquares配列要素の
   *   値（'O' または 'X'）を設定する。
   * </li>
   * <li>
   *   onClick属性 - BoardコンポーネントのプロパティのonClick
   *   関数を設定する。
   * </li>
   * </ul>
   * @param i Squareコンポーネントのインデックス。
   * @return tag Squareタグを返す。
   */
  renderSquare(i) {
    return (
      <Square
        value={this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
      />
    );
  }

  /**
   * 3 x 3 のSquareコンポーネントが配置されたBoardコンポーネントを描画する。
   * @return tag 3x3のSquareタグを返す。
   */
  render() {
    return (
      <div>
        <div className="board-row">
          {this.renderSquare(0)}
          {this.renderSquare(1)}
          {this.renderSquare(2)}
        </div>
        <div className="board-row">
          {this.renderSquare(3)}
          {this.renderSquare(4)}
          {this.renderSquare(5)}
        </div>
        <div className="board-row">
          {this.renderSquare(6)}
          {this.renderSquare(7)}
          {this.renderSquare(8)}
        </div>
      </div>
    );
  }
}

/**
 * Gameコンポーネント。
 */
class Game extends React.Component {
  /**
   * Gameコンポーネントを構築する。
   * Gameコンポーネントのプロパティに以下のプロパティを設定する。
   * <ul>
   * <li>
   *   history< - Bordコンポーネントに配置された3x3のSquareコンポーネントの
   *     表示内容の履歴の初期値として、3x3のSquareすべてにnullを設定する。
   * </li>
   * <li>
   *   stepNumber - 対局のカウンタとして0を設定する。
   * </li>
   * <li>
   *   xIsNext - true を設定する。
   * </li>
   * </ul>
   */
  constructor(props) {
    super(props);
    this.state = {
      history: [{
        squares: Array(9).fill(null),
      }],
      stepNumber: 0,
      xIsNext: true,
    };
  }

  /**
   * 指定されたインデックスのSquareコンポーネントがクリックされたときの処理を
   * 実行する関数。
   * TODO 関数の処理内容を記載する
   * @param i Squareコンポーネントのインデックス。
   */
  handleClick(i) {
    const history = this.state.history.slice(0, this.state.stepNumber + 1);
    const current = history[history.length - 1];
    const squares = current.squares.slice();
    if (calculateWinner(squares) || squares[i]) {
      return;
    }
    squares[i] = this.state.xIsNext ? 'X' : 'O';
    this.setState({
      history: history.concat([{
        squares: squares,
      }]),
      stepNumber: history.length,
      xIsNext: !this.state.xIsNext,
    });
  }

  /**
   * 指定された対局の履歴まで戻る。
   * Gameコンポーネントのプロパティを以下のように設定する。
   * <ul>
   * <li>
   *   stepNumber - step引数の値
   * </li>
   * <li>
   *   xIsNext - step引数が偶数の場合はtrue、そうでない場合はfalse
   * </li>
   * </ul>
   * @param step 履歴のインデックスを指定する。
   */
  jumpTo(step) {
    this.setState({
      stepNumber: step,
      xIsNext: (step %2) === 0,
    });
  }

  /**
   * Gameコンポーネントを描画する。
   * TODO 処理内容を記載する。
   * @return tag Bordコンポーネントと対局履歴を配置したdivタグを返す。
   */
  render() {
    const history = this.state.history;
    const current = history[this.state.stepNumber];
    const winner = calculateWinner(current.squares);

    const moves = history.map((step, move) => {
      const desc = move ? 'Go to move #' + move : 'Go to game start';
      return (
        <li key={move}>
          <button onClick={() => this.jumpTo(move)}>{desc}</button>
        </li>
      );
    });

    let status;
    if (winner) {
      status = 'Winner: ' + winner;
    } else {
      status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O');
    }

    return (
      <div className="game">
        <div className="game-board">
          <Board
            squares={current.squares}
            onClick={(i) => this.handleClick(i)}
          />
        </div>
        <div className="game-info">
          <div>{status}</div>
          <ol>{moves}</ol>
        </div>
      </div>
    );
  }
}

// ========================================
/**
 * 勝者の判定をする関数。
 * @param suquares 3x3のSquareコンポーネントに表示される記号の配列。
 * @return String 勝者が判定できた場合は勝者の記号('O'または'X')を返す。
 *   勝者が判定出来ない場合はnullを返す。
 */
function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  return null;
}

// ========================================

//const root = ReactDOM.createRoot(document.getElementById("root"));
//root.render(<Game />);
