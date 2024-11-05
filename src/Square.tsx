import React, { useLayoutEffect, useRef } from "react";
import { IPuzzle, ISquare } from "./Interfaces";
import wavingFlag from "./assets/flag.gif";
import { SoundLoader } from "./SoundLoader";

export interface SquareClassProps {
  isMine: boolean;
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
}

export interface SquareComponentProps {
  square: SquareClass;
  puzzle: IPuzzle;
  isMobile: boolean;
  updatePuzzle: (newPuzzle?: IPuzzle) => void;
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
    const directions = [
      { x: -1, y: -1 },
      { x: -1, y: 0 },
      { x: -1, y: 1 },
      { x: 0, y: -1 },
      { x: 0, y: 1 },
      { x: 1, y: -1 },
      { x: 1, y: 0 },
      { x: 1, y: 1 },
    ];
    for (const dir of directions) {
      const newX = i + dir.x;
      const newY = j + dir.y;
      if (newX >= 0 && newX < puzzle.width && newY >= 0 && newY < puzzle.height) {
        neighbors.push(puzzle.squares[newY][newX]);
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

function getMineCountColor(mineCount: number) {
  switch (mineCount) {
    case 1:
      return "blue";
    case 2:
      return "green";
    case 3:
      return "red";
    case 4:
      return "purple";
    case 5:
      return "maroon";
    case 6:
      return "turquoise";
    case 7:
      return "black";
    case 8:
      return "gray";
    default:
      return "black";
  }
}

export const SquareComponent: React.FC<SquareComponentProps> = ({
  square,
  puzzle,
  isMobile,
  updatePuzzle,
}) => {
  const [mySize, setMySize] = React.useState(10);
  const squareRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    if (squareRef.current) {
      const { width } = squareRef.current.getBoundingClientRect();
      setMySize(width);
    }
  }, [squareRef.current]);

  const mineCount = square.numMines(puzzle);
  function handleHoverStart(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    if (puzzle.status == "in progress" && !isMobile) {
      e.currentTarget.style.transform = "scale(1.2)";
      e.currentTarget.style.zIndex = "10";
      SoundLoader.hover; // Play the hover sound
    }
  }
  function handleHoverEnd(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    e.currentTarget.style.transform = "scale(1)";
    e.currentTarget.style.zIndex = "1";
  }
  function handleSelect() {
    if (puzzle.status !== "in progress") {
      return;
    }
    if (square.flagged) {
      if (isMobile) {
        puzzle.flagSquare(square);
        updatePuzzle();
      }
      return;
    }
    let wasSafeMove = true;
    if (square.revealed) {
      const flagCount = square.neighbors(puzzle).filter((n) => n.flagged).length;
      if (mineCount === flagCount && mineCount > 0) {
        square.neighbors(puzzle).forEach((n) => {
          if (!n.revealed && !n.flagged) {
            wasSafeMove = puzzle.reveal(n);
          }
        });
      }
    } else {
      if (isMobile) {
        puzzle.flagSquare(square);
      } else {
        wasSafeMove = puzzle.reveal(square);
      }
    }
    updatePuzzle();
    if (!wasSafeMove) {
      // reveal whole board!
      SoundLoader.bigPop;
      setTimeout(() => {
        for (let i = 0; i < puzzle.width; i++) {
          for (let j = 0; j < puzzle.height; j++) {
            if (puzzle.squares[j][i].revealed == false) {
              const manhattanDistance =
                Math.abs(i - square.position.x) + Math.abs(j - square.position.y);
              setTimeout(() => {
                puzzle.squares[j][i].revealed = true;
                puzzle.squares[j][i].flagged = false;
                SoundLoader.smallPop;
                updatePuzzle();
              }, manhattanDistance * 200 + 200 * Math.random());
            }
          }
        }
      }, 1000);
    } else {
      SoundLoader.select;
    }
  }
  function handleFlag(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    e.preventDefault();
    if (square.revealed) {
      return;
    }
    if (isMobile) {
      if (!square.flagged) {
        puzzle.reveal(square);
      }
    } else {
      puzzle.flagSquare(square);
    }
    updatePuzzle();
  }
  function getActualMineState() {
    if (puzzle.status == "won") {
      square.isMineHidden = false;
      const isAMine = square.isMine;
      square.isMineHidden = true;
      return isAMine;
    }
    return null;
  }
  return (
    <div
      ref={squareRef}
      style={{
        flex: 1,
        aspectRatio: "1/1",
        backgroundColor:
          puzzle.status == "won"
            ? getActualMineState()
              ? "#00AA33"
              : "lightgreen"
            : square.isMine && square.revealed
            ? "red"
            : square.revealed
            ? "white"
            : "#BBBBBB",
        border: "1px solid black",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        boxShadow: "inset 0 0 2px #222222, 0 0 2px #222222",
        borderRadius: "5px",
        cursor: puzzle.status == "in progress" ? "pointer" : undefined,
        transition: "transform 0.1s ease-in-out, z-index 0.1s ease-in-out",
        zIndex: 1,
      }}
      onMouseEnter={handleHoverStart}
      onMouseLeave={handleHoverEnd}
      onClick={handleSelect}
      onContextMenu={handleFlag}
    >
      <p
        style={{
          color: square.isMine ? "red" : getMineCountColor(mineCount),
          fontWeight: "bold",
          fontSize: `${Math.floor(mySize / 2)}px`,
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
  coords: { x: number; y: number };
  puzzle: IPuzzle;
  updatePuzzle: (newPuzzle: IPuzzle) => void;
}

export const StartSquareComponent: React.FC<StartSquareComponentProps> = ({
  coords,
  puzzle,
  updatePuzzle,
}) => {
  return (
    <div
      style={{
        flex: 1,
        aspectRatio: "1/1",
        backgroundColor: "#BBBBBB",
        border: "1px solid black",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        boxShadow: "inset 0 0 2px #222222, 0 0 2px #222222",
        borderRadius: "5px",
        cursor: "pointer",
        transition: "transform 0.1s ease-in-out, z-index 0.1s ease-in-out",
        zIndex: 1,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "scale(1.1)";
        e.currentTarget.style.zIndex = "10";
        SoundLoader.hover;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "scale(1)";
        e.currentTarget.style.zIndex = "1";
      }}
      onClick={() => {
        const newPuzzle = puzzle.initialize(coords);
        SoundLoader.select;
        updatePuzzle(newPuzzle);
      }}
    />
  );
};
