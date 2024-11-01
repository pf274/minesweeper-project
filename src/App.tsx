import { useState } from "react";
import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";

function App() {
  const [puzzle, setPuzzle] = useState(new PuzzleClass({ width: 9, height: 9, totalMines: 10 }));

  const updatePuzzle = (newPuzzle?: PuzzleClass) => {
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
