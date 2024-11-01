import { useState } from "react";
import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";
import { IPuzzle } from "./Interfaces";

function App() {
  const [puzzle, setPuzzle] = useState<IPuzzle>(
    new PuzzleClass({ width: 10, height: 10, totalMines: 0.2 })
  );

  const updatePuzzle = (newPuzzle?: IPuzzle) => {
    if (newPuzzle) {
      setPuzzle(newPuzzle);
    } else {
      setPuzzle(
        new PuzzleClass({
          width: puzzle.width,
          height: puzzle.height,
          totalMines: puzzle.totalMines,
          squares: puzzle.squares,
          initialized: puzzle.initialized,
          status: puzzle.status,
        })
      );
    }
  };

  return (
    <>
      <h1>Minesweeper</h1>
      <div className="card">
        <PuzzleComponent puzzle={puzzle} updatePuzzle={updatePuzzle} />
      </div>
    </>
  );
}

export default App;
