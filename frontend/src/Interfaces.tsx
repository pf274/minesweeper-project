export interface ISquare {
  revealed: boolean;
  flagged: boolean;
  position: { x: number; y: number };
  isMine: boolean | null;
  highlighted: boolean;
  neighbors(puzzle: IPuzzle): ISquare[];
  numMines(puzzle: IPuzzle): number;
}

export interface IPuzzle {
  width: number;
  height: number;
  totalMines: number;
  startX: number;
  startY: number;
  squares: ISquare[][];
  status: "not started" | "in progress" | "won" | "lost";
  initialized: boolean;
  highlightHintCells(hint: HintType): void;
  reveal(square: ISquare): boolean;
  flagSquare(square: ISquare): void;
  initialize(coords: { x: number; y: number }): Promise<IPuzzle>;
  checkWin(): void;
}

export type HintType =
  | {
      active: boolean;
      text: string;
      hiddenCellsToHighlight: [number, number][];
      revealedCellsToHighlight: [number, number][];
    }[]
  | null;
