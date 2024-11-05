export interface ISquare {
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
  isMine: boolean | null;
  neighbors(puzzle: IPuzzle): ISquare[];
  numMines(puzzle: IPuzzle): number;
}

export interface IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  squares: ISquare[][];
  status: "not started" | "in progress" | "won" | "lost";
  initialized: boolean;
  reveal(square: ISquare): boolean;
  flagSquare(square: ISquare): void;
  initialize(coords: { x: number; y: number }): IPuzzle;
  checkWin(): void;
}
