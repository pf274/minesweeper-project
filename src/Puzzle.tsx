import { Button } from "@mui/material";
import { IPuzzle, ISquare } from "./Interfaces";
import { SquareClass, SquareComponent, StartSquareComponent } from "./Square";

interface PuzzleClassProps {
  width: number;
  height: number;
  totalMines: number;
  squares?: ISquare[][];
  initialized?: boolean;
  status?: "not started" | "in progress" | "won" | "lost";
}

interface PuzzleComponentProps {
  puzzle: PuzzleClass;
  updatePuzzle: (newPuzzle?: IPuzzle) => void;
}

export class PuzzleClass implements IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  squares: ISquare[][];
  initialized: boolean;
  status: "not started" | "in progress" | "won" | "lost";
  constructor({
    width,
    height,
    totalMines,
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
    squares.forEach((s) => (s.isMineHidden = false));
    const mines = squares.filter((s) => s.isMine);
    squares.forEach((s) => (s.isMineHidden = true));
    if (unrevealedSquares.length == mines.length) {
      this.status = "won";
      console.log("You win!");
      SoundLoader.win1;
    }
  }

  public flagSquare(square: ISquare) {
    square.flagged = !square.flagged;
  }
  public initialize(coords: { x: number; y: number }): PuzzleClass {
    let remainingMines = this.totalMines;
    let remainingPositions: { x: number; y: number }[] = [];
    for (let i = 0; i < this.width; i++) {
      for (let j = 0; j < this.height; j++) {
        remainingPositions.push({ x: i, y: j });
      }
    }
    const startingPositions = remainingPositions.filter((s) => {
      return (Math.abs(s.x - coords.x) <= 1 && Math.abs(s.y - coords.y) <= 1) == true;
    });
    remainingPositions = remainingPositions.filter((s) => {
      return (Math.abs(s.x - coords.x) <= 1 && Math.abs(s.y - coords.y) <= 1) == false;
    });
    const newBoard = new Array(this.height).fill(null).map(() => new Array(this.width).fill(null));

    while (remainingPositions.length > 0) {
      const pos = remainingPositions.shift()!;
      const remainingSquares = remainingPositions.length;
      const newSquare = new SquareClass({
        isMine: Math.random() < remainingMines / remainingSquares,
        revealed: false,
        flagged: false,
        position: pos,
        isMineHidden: false,
      });
      if (newSquare.isMine) {
        remainingMines--;
      }
      newSquare.isMineHidden = true;
      newBoard[pos.y][pos.x] = newSquare;
    }
    for (const pos of startingPositions) {
      const newSquare = new SquareClass({
        isMine: false,
        revealed: false,
        flagged: false,
        position: pos,
        isMineHidden: true,
      });
      newBoard[pos.y][pos.x] = newSquare;
    }
    this.squares = newBoard;
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
    });
  }
}

const gap = "0.1em";

import { CSSProperties } from "react";
import { SoundLoader } from "./SoundLoader";

const rowStyle: CSSProperties = {
  display: "flex",
  flexDirection: "row",
  flexWrap: "nowrap",
  gap,
};

export const PuzzleComponent: React.FC<PuzzleComponentProps> = ({ puzzle, updatePuzzle }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap }}>
      {puzzle.initialized &&
        puzzle.squares.map((row, index) => {
          return (
            <div key={index} style={rowStyle}>
              {row.map((cell, index) => (
                <SquareComponent
                  key={index}
                  size={Math.min(window.innerWidth, window.innerHeight) / puzzle.width / 2}
                  square={cell as SquareClass}
                  puzzle={puzzle}
                  updatePuzzle={updatePuzzle}
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
                size={Math.min(window.innerWidth, window.innerHeight) / puzzle.width / 2}
                coords={{ x: j, y: i }} // Ensure correct x and y coordinates
                puzzle={puzzle}
                updatePuzzle={updatePuzzle}
              />
            ))}
          </div>
        ))}

      <h2>
        {puzzle.status == "won" && "You win!"}
        {puzzle.status == "lost" && "You lose!"}
        {puzzle.status == "in progress" && "Good luck!"}
        {puzzle.status == "not started" && "Click a square to start!"}
      </h2>
      {puzzle.status != "not started" && puzzle.status != "in progress" && (
        <Button
          onClick={() =>
            updatePuzzle(
              new PuzzleClass({
                width: puzzle.width,
                height: puzzle.height,
                totalMines: puzzle.totalMines,
              })
            )
          }
        >
          Play again
        </Button>
      )}
    </div>
  );
};
