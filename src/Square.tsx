import React from "react";

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
  board: SquareClass[][];
}

export class SquareClass {
  private _isMine: boolean;
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
  constructor({
    isMine,
    revealed,
    flagged,
    position,
    isMineHidden,
  }: SquareClassProps) {
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
  neighbors(board: SquareClass[][]) {
    const neighbors = [];
    const i = this.position.x;
    const j = this.position.y;
    if (i > 0) {
      if (j > 0) {
        neighbors.push(board[i - 1][j - 1]);
      }
      neighbors.push(board[i - 1][j]);
      if (j < 8) {
        neighbors.push(board[i - 1][j + 1]);
      }
    }
    if (j > 0) {
      neighbors.push(board[i][j - 1]);
    }
    if (j < 8) {
      neighbors.push(board[i][j + 1]);
    }
    if (i < 8) {
      if (j > 0) {
        neighbors.push(board[i + 1][j - 1]);
      }
      neighbors.push(board[i + 1][j]);
      if (j < 8) {
        neighbors.push(board[i + 1][j + 1]);
      }
    }
    return neighbors;
  }
  unlockNeighbors(board: SquareClass[][]) {
    const neighbors = this.neighbors(board);
    neighbors.forEach((n) => (n.isMineHidden = false));
  }
  lockNeighbors(board: SquareClass[][]) {
    const neighbors = this.neighbors(board);
    neighbors.forEach((n) => (n.isMineHidden = true));
  }
  numMines(board: SquareClass[][]) {
    const neighbors = this.neighbors(board);
    this.unlockNeighbors(board);
    const returnVal = neighbors.filter((n) => n.isMine).length;
    this.lockNeighbors(board);
    return returnVal;
  }
  flaggedMines(board: SquareClass[][]) {
    const neighbors = this.neighbors(board);
    this.unlockNeighbors(board);
    const returnVal = neighbors.filter((n) => n.flagged && n.isMine).length;
    this.lockNeighbors(board);
    return returnVal;
  }
  unflaggedMines(board: SquareClass[][]) {
    const neighbors = this.neighbors(board);
    this.unlockNeighbors(board);
    const returnVal = neighbors.filter((n) => !n.flagged && n.isMine).length;
    this.lockNeighbors(board);
    return returnVal;
  }
}

export const SquareComponent: React.FC<SquareComponentProps> = ({
  square,
  size,
  board,
}) => {
  const mineCount = square.numMines(board);
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
      }}
    >
      <p
        style={{
          color: square.isMine ? "red" : "black",
          fontWeight: "bold",
          padding: 0,
          margin: 0,
          display:
            square.revealed && (mineCount > 0 || square.isMine)
              ? "block"
              : "none",
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
        F
      </p>
    </div>
  );
};
