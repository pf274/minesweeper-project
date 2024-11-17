import { useEffect, useState } from "react";
import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";
import { HintType, IPuzzle } from "./Interfaces";
import { Button, Snackbar } from "@mui/material";

function App() {
  const [hint, setHint] = useState<HintType>(null);
  const [hintShown, setHintShown] = useState(false);

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
          startX: puzzle.startX,
          startY: puzzle.startY,
        })
      );
    }
  };

  useEffect(() => {
    const isNewHint = hint && hint.findIndex((step) => step.active) == 0;
    if (isNewHint) {
      console.log(hint);
      setHintShown(true);
      puzzle.highlightHintCells(hint);
      updatePuzzle();
    }
  }, [hint]);
  const [puzzle, setPuzzle] = useState<IPuzzle>(
    new PuzzleClass({ width: 10, height: 10, totalMines: 30, startX: 0, startY: 0 })
  );

  function dismissHint() {
    setHint(null);
    setHintShown(false);
    puzzle.highlightHintCells(null);
  }

  function showNextHintStep() {
    if (hint == null) {
      setHintShown(false);
      return;
    }
    const currentHintStep = hint.findIndex((step) => step.active);
    const wasLastHintStep = currentHintStep == hint.length - 1;
    let newHint = null;
    if (wasLastHintStep) {
      newHint = hint.map((step, i) => {
        return {
          ...step,
          active: i == 0,
        };
      });
    } else {
      newHint = hint.map((step, i) => {
        return {
          ...step,
          active: i == currentHintStep + 1,
        };
      });
    }
    puzzle.highlightHintCells(newHint);
    setHint(newHint);
    updatePuzzle();
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", flex: 1, maxWidth: "1000px" }}>
      <h1 style={{ margin: "0.5em" }}>Minesweeper</h1>
      <PuzzleComponent puzzle={puzzle} updatePuzzle={updatePuzzle} setHint={setHint} />
      <Snackbar
        open={hintShown}
        onClose={dismissHint}
        message={hint?.find((step) => step.active)?.text || "not hint text found"}
        action={
          hint && hint.length > 1 ? (
            <Button color="inherit" size="small" onClick={showNextHintStep}>
              {hint
                ? hint.findIndex((step) => step.active) == hint.length - 1
                  ? "Restart hint"
                  : "Next"
                : "Close"}
            </Button>
          ) : undefined
        }
      />
    </div>
  );
}

export default App;
