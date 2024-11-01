export interface ISquare {
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMineHidden: boolean;
}

export interface IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  squares: ISquare[][];
  reveal(square: ISquare): void;
  flagSquare(square: ISquare): void;
  initialize(coords: { x: number; y: number }): IPuzzle;
}
