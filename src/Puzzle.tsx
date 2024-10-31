import { IPuzzle } from "./Interfaces";
import { SquareClass, SquareComponent } from "./Square";

interface PuzzleClassProps {
  width: number;
  height: number;
  totalMines: number;
  squares: SquareClass[][];
}

interface PuzzleComponentProps {
  puzzle: PuzzleClass;
}

export class PuzzleClass implements IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  squares: SquareClass[][];
  constructor({ width, height, totalMines, squares }: PuzzleClassProps) {
    this.width = width;
    this.height = height;
    this.totalMines = totalMines;
    this.squares = squares;
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
}

const gap = "0.1em";

export const PuzzleComponent: React.FC<PuzzleComponentProps> = ({ puzzle }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap }}>
      {puzzle.squares.map((row, index) => {
        return (
          <div
            key={index}
            style={{
              display: "flex",
              flexDirection: "row",
              flexWrap: "nowrap",
              gap,
            }}
          >
            {row.map((cell, index) => (
              <SquareComponent
                key={index}
                size={Math.min(window.innerWidth, window.innerHeight) / puzzle.width / 2}
                square={cell}
                puzzle={puzzle}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};
