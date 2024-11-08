import { useState } from "react";
import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";
import { IPuzzle } from "./Interfaces";

function App() {
  const [puzzle, setPuzzle] = useState<IPuzzle>(
    new PuzzleClass({ width: 10, height: 10, totalMines: 10 })
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
    <div style={{ display: "flex", flexDirection: "column", flex: 1, maxWidth: "1000px" }}>
      <h1 style={{ margin: "0.5em" }}>Minesweeper</h1>
      <PuzzleComponent puzzle={puzzle} updatePuzzle={updatePuzzle} />
    </div>
  );
}

export default App;
