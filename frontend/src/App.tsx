import { useEffect, useState } from "react";
import "./App.css";
import { PuzzleClass, PuzzleComponent } from "./Puzzle";
import { HintType, IPuzzle } from "./Interfaces";
import {
  Button,
  darken,
  Dialog,
  DialogContent,
  DialogTitle,
  List,
  ListItemButton,
  Snackbar,
  Typography,
  useTheme,
} from "@mui/material";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import CloseIcon from "@mui/icons-material/Close";
import FastRewindIcon from "@mui/icons-material/FastRewind";

function App() {
  const [hint, setHint] = useState<HintType>(null);
  const [hintShown, setHintShown] = useState(false);
  const [puzzleSelectionShown, setPuzzleSelectionShown] = useState(false);
  const theme = useTheme();

  function handlePuzzleSelection(width: number, height: number, totalMines: number) {
    const newPuzzle = new PuzzleClass({ width, height, totalMines, startX: 0, startY: 0 });
    updatePuzzle(newPuzzle);
    setPuzzleSelectionShown(false);
  }

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
  function showPuzzleSelection() {
    setPuzzleSelectionShown(true);
  }

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
    new PuzzleClass({ width: 9, height: 9, totalMines: 35, startX: 0, startY: 0 })
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
    <div style={{ flex: 1 }}>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          flex: 1,
        }}
      >
        <h1 style={{ margin: 0, marginTop: "0.5em" }}>Minesweeper</h1>
        <PuzzleComponent
          puzzle={puzzle}
          updatePuzzle={updatePuzzle}
          setHint={setHint}
          showPuzzleSelection={showPuzzleSelection}
        />
        <Snackbar open={hintShown} onClose={dismissHint}>
          <div
            style={{
              backgroundColor: theme.palette.secondary.dark,
              color: theme.palette.secondary.contrastText,
              padding: "0.25em",
              paddingLeft: "0.5em",
              borderRadius: "5px",
              alignItems: "center",
              display: "flex",
              justifyContent: "space-between",
              gap: "0.5em",
            }}
          >
            <Typography>
              {hint?.find((step) => step.active)?.text || "not hint text found"}
            </Typography>
            {hint && hint.length > 1 ? (
              <Button
                variant="contained"
                sx={{
                  backgroundColor: darken(theme.palette.secondary.dark, 0.4),
                  color: theme.palette.secondary.contrastText,
                }}
                size="small"
                onClick={showNextHintStep}
              >
                {hint ? (
                  hint.findIndex((step) => step.active) == hint.length - 1 ? (
                    <FastRewindIcon />
                  ) : (
                    <ArrowForwardIosIcon />
                  )
                ) : (
                  <CloseIcon />
                )}
              </Button>
            ) : undefined}
          </div>
        </Snackbar>
        <Dialog open={puzzleSelectionShown} onClose={() => setPuzzleSelectionShown(false)}>
          <DialogTitle>Choose a Puzzle</DialogTitle>
          <DialogContent>
            <List
              style={{
                maxHeight: "40vh",
                overflowY: "auto",
                backgroundColor: theme.palette.grey[300],
                borderRadius: "5px",
              }}
            >
              <ListItemButton onClick={() => handlePuzzleSelection(9, 9, 10)}>
                9x9, 10 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(9, 9, 35)}>
                9x9, 35 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(16, 16, 40)}>
                16x16, 40 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(16, 16, 99)}>
                16x16, 99 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(30, 16, 99)}>
                30x16, 99 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(30, 16, 170)}>
                30x16, 170 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(16, 30, 99)}>
                16x30, 99 mines
              </ListItemButton>
              <ListItemButton onClick={() => handlePuzzleSelection(16, 30, 170)}>
                16x30, 170 mines
              </ListItemButton>
            </List>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

export default App;
