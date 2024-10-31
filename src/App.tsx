import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import { SquareClass } from "./Square";

import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";

function generatePuzzle() {
  const board = new PuzzleClass({
    width: 9,
    height: 9,
    totalMines: 10,
    squares: [],
  });
  let remainingMines = board.totalMines;
  for (let i = 0; i < 9; i++) {
    const newRow = [];
    for (let j = 0; j < 9; j++) {
      const remainingSquares = 9 * 9 - (i * 9 + j);
      const newSquare = new SquareClass({
        isMine: Math.random() < remainingMines / remainingSquares,
        revealed: false,
        flagged: false,
        position: { x: i, y: j },
        isMineHidden: true,
      });
      if (newSquare.isMine) {
        remainingMines--;
      }
      newRow.push(newSquare);
    }
    board.squares.push(newRow);
  }
  return board;
}

function App() {
  const [puzzle] = useState(generatePuzzle());

  return (
    <>
      <h1>Minesweeper</h1>
      <div className="card">
        <PuzzleComponent puzzle={puzzle} />
      </div>
    </>
  );
}

export default App;
