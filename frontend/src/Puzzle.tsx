import { Button, Switch, Typography } from "@mui/material";
import { HintType, IPuzzle, ISquare } from "./Interfaces";
import { SquareClass, SquareComponent, StartSquareComponent } from "./Square";
import { CSSProperties, useEffect, useRef } from "react";
import { SoundLoader } from "./SoundLoader";
import axios from "axios";
import { useState } from "react";

interface PuzzleClassProps {
  width: number;
  height: number;
  totalMines: number;
  startX: number;
  startY: number;
  squares?: ISquare[][];
  initialized?: boolean;
  status?: "not started" | "in progress" | "won" | "lost";
}

interface PuzzleComponentProps {
  puzzle: PuzzleClass;
  updatePuzzle: (newPuzzle?: IPuzzle) => void;
  setHint: (hint: any) => void;
  showPuzzleSelection: () => void;
}

export class PuzzleClass implements IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  startX: number;
  startY: number;
  squares: ISquare[][];
  initialized: boolean;
  status: "not started" | "in progress" | "won" | "lost";
  constructor({
    width,
    height,
    totalMines,
    startX,
    startY,
    squares = [],
    initialized = false,
    status = "not started",
  }: PuzzleClassProps) {
    this.width = width;
    this.height = height;
    this.totalMines = totalMines;
    this.squares = squares;
    this.initialized = initialized;
    this.status = status;
    this.startX = startX;
    this.startY = startY;
  }
  public reveal(square: ISquare): boolean {
    square.revealed = true;
    if (square.isMine) {
      this.status = "lost";
      console.log("You lose!");
      SoundLoader.bigPop;
      setTimeout(() => {
        SoundLoader.oof;
        setTimeout(() => {
          SoundLoader.disappointment;
        }, 700);
      }, 200);
      return false;
    } else if (square.numMines(this) == 0) {
      const squaresToReveal = new Set(square.neighbors(this).filter((n) => !n.revealed));
      while (squaresToReveal.size > 0) {
        for (const sq of squaresToReveal.values()) {
          sq.revealed = true;
          if (sq.numMines(this) == 0) {
            const neighbors = sq.neighbors(this).filter((n) => !n.revealed);
            neighbors.forEach((n) => squaresToReveal.add(n));
          }
          squaresToReveal.delete(sq);
        }
      }
    }
    this.checkWin();
    return true;
  }
  public checkWin() {
    const squares = this.squares.flat();
    const unrevealedSquares = squares.filter((s) => !s.revealed);
    const mines = squares.filter((s) => s.isMine);
    if (unrevealedSquares.length == mines.length) {
      this.status = "won";
      console.log("You win!");
      SoundLoader.win1;
    }
  }

  public flagSquare(square: ISquare) {
    square.flagged = !square.flagged;
  }
  public async initialize(coords: { x: number; y: number }): Promise<PuzzleClass> {
    const returnedBoard = await axios.get(
      "https://tzirp8okm0.execute-api.us-east-1.amazonaws.com/dev/genboard",
      {
        params: {
          width: this.width,
          height: this.height,
          mines: this.totalMines,
          startX: coords.x,
          startY: coords.y,
        },
      }
    );
    const retrievedGrid = returnedBoard.data.board.grid;
    const parsedBoard = new Array(this.height)
      .fill(null)
      .map(() => new Array(this.width).fill(null));
    for (let i = 0; i < this.height; i++) {
      for (let j = 0; j < this.width; j++) {
        const newSquare = new SquareClass({
          isMine: retrievedGrid[i][j].isMine,
          revealed: retrievedGrid[i][j].isVisible,
          flagged: retrievedGrid[i][j].isFlagged,
          position: { x: j, y: i },
        });
        parsedBoard[i][j] = newSquare;
      }
    }
    this.squares = parsedBoard;
    this.initialized = true;
    this.status = "in progress";
    this.reveal(this.squares[coords.y][coords.x]);
    SoundLoader.backgroundMusic;
    return new PuzzleClass({
      width: this.width,
      height: this.height,
      totalMines: this.totalMines,
      squares: this.squares,
      initialized: this.initialized,
      status: this.status,
      startX: coords.x,
      startY: coords.y,
    });
  }
  public highlightHintCells(hint: HintType) {
    this.squares.flat().forEach((square) => {
      square.highlighted = false;
    });
    if (hint) {
      hint.forEach((step) => {
        if (step.active) {
          step.revealedCellsToHighlight.forEach(([x, y]) => {
            this.squares[y][x].highlighted = true;
          });
          step.hiddenCellsToHighlight.forEach(([x, y]) => {
            this.squares[y][x].highlighted = true;
          });
        }
      });
    }
  }
}

const gap = 0.1;

const rowStyle: CSSProperties = {
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap",
  gap: `${gap}em`,
  width: "100%",
};

const mobileLimit = 1000;

export const PuzzleComponent: React.FC<PuzzleComponentProps> = ({
  puzzle,
  updatePuzzle,
  setHint,
  showPuzzleSelection,
}) => {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= mobileLimit);
  const [maxHeightOfGrid, setMaxHeightOfGrid] = useState("100vh");
  const gridRef = useRef<HTMLDivElement>(null);
  function updateMaxHeightOfGrid() {
    if (gridRef.current) {
      const rect = gridRef.current.getBoundingClientRect();
      const newMaxHeight = `calc(100vh - ${rect.top}px - 4em)`;
      setMaxHeightOfGrid(newMaxHeight);
    }
  }
  useEffect(() => {
    updateMaxHeightOfGrid();
    window.addEventListener("resize", updateMaxHeightOfGrid);
    return () => window.removeEventListener("resize", updateMaxHeightOfGrid);
  }, [puzzle]);
  async function handleGetHint() {
    const squares = puzzle.squares.map((row) =>
      row.map((cell) => ({
        isMine: cell.isMine,
        isVisible: cell.revealed,
        isFlagged: cell.flagged,
        location: [cell.position.x, cell.position.y],
      }))
    );
    const requestBody = {
      grid: squares,
      width: puzzle.width,
      height: puzzle.height,
      mines: puzzle.totalMines,
      startX: puzzle.startX,
      startY: puzzle.startY,
    };
    const hintResponse = await axios.post(
      "https://tzirp8okm0.execute-api.us-east-1.amazonaws.com/dev/hint",
      requestBody
    );
    let hintData = hintResponse?.data?.hint;
    if (!hintData) {
      console.log("No hint data found");
      return;
    }
    if (!Array.isArray(hintData)) {
      console.log("Invalid hint data");
      return;
    }
    if (hintData.length < 1) {
      console.log("No hint data found");
      return;
    }
    hintData = hintData.map((hintStep, index) => ({
      ...hintStep,
      active: index == 0,
    }));
    setHint(hintData);
    puzzle.highlightHintCells(hintData);
    updatePuzzle();
  }
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-start",
        alignItems: "center",
      }}
    >
      <h2 style={{ margin: "0.25em" }}>
        {puzzle.status == "won" && "You win!"}
        {puzzle.status == "lost" && "You lose!"}
        {puzzle.status == "in progress" && "Good luck!"}
        {puzzle.status == "not started" && "Click a square to start!"}
      </h2>
      <h2 style={{ margin: 0 }}>
        {puzzle.status == "in progress" &&
          `Mines left: ${
            puzzle.totalMines - puzzle.squares.flat().filter((s) => s.flagged).length
          }`}
      </h2>
      <div style={{ paddingLeft: "1em", paddingRight: "1em", paddingBottom: "1em" }}>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between",
            width: "100%",
            alignItems: "center",
            gap: "0.5em",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              flexWrap: "wrap",
              justifyContent: "center",
            }}
          >
            <Typography>Mobile Mode</Typography>
            <Switch color="success" checked={isMobile} onChange={() => setIsMobile(!isMobile)} />
          </div>
          {puzzle.initialized && (
            <Button color="primary" variant="contained" onClick={handleGetHint}>
              Get Hint
            </Button>
          )}
          <Button color="secondary" variant="contained" onClick={showPuzzleSelection}>
            Change Puzzle
          </Button>
        </div>
      </div>
      {puzzle.status != "not started" && puzzle.status != "in progress" && (
        <Button
          onClick={() =>
            updatePuzzle(
              new PuzzleClass({
                width: puzzle.width,
                height: puzzle.height,
                totalMines: puzzle.totalMines,
                startX: puzzle.startX,
                startY: puzzle.startY,
              })
            )
          }
          variant="contained"
        >
          Play again
        </Button>
      )}
      <div // container for the grid
        ref={gridRef}
        style={{
          display: "flex",
          flexDirection: "column",
          padding: "0.5em",
          gap: `${gap}em`,
          maxWidth: `calc(100vw - 1em - ${gap * puzzle.width}em)`,
          maxHeight: maxHeightOfGrid,
          overflow: "auto",
        }}
      >
        {puzzle.initialized &&
          puzzle.squares.map((row, index) => {
            return (
              <div key={index} style={rowStyle}>
                {row.map((cell, index) => (
                  <SquareComponent
                    key={index}
                    square={cell as SquareClass}
                    puzzle={puzzle}
                    updatePuzzle={updatePuzzle}
                    isMobile={isMobile}
                  />
                ))}
              </div>
            );
          })}
        {!puzzle.initialized &&
          new Array(puzzle.height).fill(null).map((_, i) => (
            <div key={`row_${i}`} style={rowStyle}>
              {new Array(puzzle.width).fill(null).map((_, j) => (
                <StartSquareComponent
                  key={`square_${i * puzzle.width + j}`}
                  coords={{ x: j, y: i }} // Ensure correct x and y coordinates
                  puzzle={puzzle}
                  updatePuzzle={updatePuzzle}
                />
              ))}
            </div>
          ))}
      </div>
    </div>
  );
};
