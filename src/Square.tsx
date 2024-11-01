import React, { useEffect, useState } from "react";
import { IPuzzle, ISquare } from "./Interfaces";
import wavingFlag from "./assets/flag.gif";

export interface SquareClassProps {
  isMine: boolean;
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
}

export interface SquareComponentProps {
  square: SquareClass;
  size: number;
  puzzle: IPuzzle;
  updatePuzzle: () => void;
}

export class SquareClass implements ISquare {
  private _isMine: boolean;
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
  constructor({ isMine, revealed, flagged, position, isMineHidden }: SquareClassProps) {
    this._isMine = isMine;
    this.isMineHidden = isMineHidden;
    this.revealed = revealed;
    this.flagged = flagged;
    this.position = position;
  }
  get isMine() {
    if (this.isMineHidden && !this.revealed) {
      return null;
    } else {
      return this._isMine;
    }
  }
  neighbors(puzzle: IPuzzle) {
    const neighbors = [];
    const i = this.position.x;
    const j = this.position.y;
    if (i > 0) {
      if (j > 0) {
        neighbors.push(puzzle.squares[i - 1][j - 1]);
      }
      neighbors.push(puzzle.squares[i - 1][j]);
      if (j < 8) {
        neighbors.push(puzzle.squares[i - 1][j + 1]);
      }
    }
    if (j > 0) {
      neighbors.push(puzzle.squares[i][j - 1]);
    }
    if (j < 8) {
      neighbors.push(puzzle.squares[i][j + 1]);
    }
    if (i < 8) {
      if (j > 0) {
        neighbors.push(puzzle.squares[i + 1][j - 1]);
      }
      neighbors.push(puzzle.squares[i + 1][j]);
      if (j < 8) {
        neighbors.push(puzzle.squares[i + 1][j + 1]);
      }
    }
    return neighbors as SquareClass[];
  }
  unlockNeighbors(puzzle: IPuzzle) {
    const neighbors = this.neighbors(puzzle);
    neighbors.forEach((n) => (n.isMineHidden = false));
  }
  lockNeighbors(puzzle: IPuzzle) {
    const neighbors = this.neighbors(puzzle);
    neighbors.forEach((n) => (n.isMineHidden = true));
  }
  numMines(puzzle: IPuzzle) {
    const neighbors = this.neighbors(puzzle);
    this.unlockNeighbors(puzzle);
    const returnVal = neighbors.filter((n) => n.isMine).length;
    this.lockNeighbors(puzzle);
    return returnVal;
  }
  flaggedMines(puzzle: IPuzzle) {
    const neighbors = this.neighbors(puzzle);
    this.unlockNeighbors(puzzle);
    const returnVal = neighbors.filter((n) => n.flagged && n.isMine).length;
    this.lockNeighbors(puzzle);
    return returnVal;
  }
  unflaggedMines(puzzle: IPuzzle) {
    const neighbors = this.neighbors(puzzle);
    this.unlockNeighbors(puzzle);
    const returnVal = neighbors.filter((n) => !n.flagged && n.isMine).length;
    this.lockNeighbors(puzzle);
    return returnVal;
  }
}

export const SquareComponent: React.FC<SquareComponentProps> = ({
  square,
  size,
  puzzle,
  updatePuzzle,
}) => {
  const mineCount = square.numMines(puzzle);
  return (
    <div
      style={{
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: square.revealed ? "white" : "#BBBBBB",
        border: "1px solid black",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        boxShadow: "inset 0 0 2px #222222, 0 0 2px #222222",
        borderRadius: "5px",
        cursor: "pointer",
      }}
      onClick={() => {
        if (square.revealed) {
          const numMines = square.numMines(puzzle);
          const flaggedMines = square.flaggedMines(puzzle);
          if (numMines === flaggedMines) {
            square.neighbors(puzzle).forEach((n) => {
              if (!n.revealed && !n.flagged) {
                puzzle.reveal(n);
              }
            });
          }
        } else {
          puzzle.reveal(square);
        }
        updatePuzzle();
      }}
      onContextMenu={(e) => {
        e.preventDefault();
        if (square.revealed) {
          return;
        }
        puzzle.flagSquare(square);
        updatePuzzle();
      }}
    >
      <p
        style={{
          color: square.isMine ? "red" : "black",
          fontWeight: "bold",
          padding: 0,
          margin: 0,
          display: square.revealed && (mineCount > 0 || square.isMine) ? "block" : "none",
        }}
      >
        {square.isMine ? "X" : mineCount}
      </p>
      <p
        style={{
          color: "red",
          fontWeight: "bold",
          padding: 0,
          margin: 0,
          display: square.flagged ? "block" : "none",
        }}
      >
        <img
          src={wavingFlag}
          alt="flag"
          style={{ width: "80%", height: "80%", display: "block", margin: "auto" }}
        />
      </p>
    </div>
  );
};

interface StartSquareComponentProps {
  size: number;
  coords: { x: number; y: number };
  puzzle: IPuzzle;
  updatePuzzle: (newPuzzle: IPuzzle) => void;
}

export const StartSquareComponent: React.FC<StartSquareComponentProps> = ({
  size,
  coords,
  puzzle,
  updatePuzzle,
}) => {
  return (
    <div
      style={{
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: "#BBBBBB",
        border: "1px solid black",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        boxShadow: "inset 0 0 2px #222222, 0 0 2px #222222",
        borderRadius: "5px",
        cursor: "pointer",
      }}
      onClick={() => {
        const newPuzzle = puzzle.initialize(coords);
        updatePuzzle(newPuzzle);
      }}
    />
  );
};
