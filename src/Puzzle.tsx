import { IPuzzle } from "./Interfaces";
import { SquareClass, SquareComponent, StartSquareComponent } from "./Square";

interface PuzzleClassProps {
  width: number;
  height: number;
  totalMines: number;
  squares?: SquareClass[][];
  initialized?: boolean;
}

interface PuzzleComponentProps {
  puzzle: PuzzleClass;
  updatePuzzle: () => void;
}

export class PuzzleClass implements IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  squares: SquareClass[][];
  initialized: boolean;
  constructor({ width, height, totalMines, squares = [], initialized = false }: PuzzleClassProps) {
    this.width = width;
    this.height = height;
    this.totalMines = totalMines;
    this.squares = squares;
    this.initialized = initialized;
  }
  public reveal(square: SquareClass) {
    square.revealed = true;
    if (square.isMine) {
      console.log("Game Over!");
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
  }
  public flagSquare(square: SquareClass) {
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
    const newBoard = new Array(this.width).fill(null).map(() => new Array(this.height).fill(null));

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
      newBoard[pos.x][pos.y] = newSquare;
    }
    for (const pos of startingPositions) {
      const newSquare = new SquareClass({
        isMine: false,
        revealed: false,
        flagged: false,
        position: pos,
        isMineHidden: true,
      });
      newBoard[pos.x][pos.y] = newSquare;
    }
    this.squares = newBoard;
    this.initialized = true;
    this.reveal(this.squares[coords.x][coords.y]);
    return new PuzzleClass({
      width: this.width,
      height: this.height,
      totalMines: this.totalMines,
      squares: this.squares,
      initialized: this.initialized,
    });
  }
}

const gap = "0.1em";

import { CSSProperties } from "react";

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
                  square={cell}
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
                coords={{ x: i, y: j }}
                puzzle={puzzle}
                updatePuzzle={updatePuzzle}
              />
            ))}
          </div>
        ))}
    </div>
  );
};
