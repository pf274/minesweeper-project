import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.classes.Board import Board
from src.classes.Cell import Cell
from src.moves import FlagRemainingNeighbors, RevealCell, ExpandCell, FlagCells, Move

def getFlagRemainingCellMove(board: Board) -> FlagRemainingNeighbors:
  """
  Attempts to find an cell where all unrevealed neighbors must be mines.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    FlagRemainingNeighbors: The move to place flags on the unrevealed neighbors, or None if no move is found.
  """
  # TODO: Implement this move
  pass

def getExpandCellMove(board: Board) -> ExpandCell:
  """
  Attempts to find an cell where all remaining neighbors are safe.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    ExpandCell: The move to reveal safe neighbors, or None if no move is found.
  """
  # TODO: Implement this move
  pass

def getRevealCellMove(board: Board) -> RevealCell:
  """
  Attempts to find a cell where all its mines have been flagged.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    RevealCell: The move to reveal the cell, or None if no move is found.
  """
  # TODO: Implement this move
  pass

def pairCoords(x: int, y: int):
  """
  Returns the coordinates in a 5x5 grid around the given coordinates, not including the center.
  """
  return [
    (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
    (x - 1, y), (x + 1, y),
    (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
    (x - 2, y - 2), (x - 1, y - 2), (x, y - 2), (x + 1, y - 2), (x + 2, y - 2),
    (x - 2, y - 1), (x + 2, y - 1),
    (x - 2, y), (x + 2, y),
    (x - 2, y + 1), (x + 2, y + 1),
    (x - 2, y + 2), (x - 1, y + 2), (x, y + 2), (x + 1, y + 2), (x + 2, y + 2)
  ]

def getSetIntersectionFlagMove(board: Board) -> FlagCells:
  """
  Attempts to find a pair of cells where the intersection of their neighbors reveals the location of mines.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    FlagCells: The move to flag the cells, or None if no move is found.
  """
  # TODO: FIX THIS FUNCTION!
  for y in range(board.height):
    for x in range(board.width):
      cell = board.grid[y][x]
      numMines1 = board.cellMinesNum(cell)
      numFlags1 = board.cellFlagsNum(cell)
      if cell.isVisible and numMines1 > 0 and numMines1 != numFlags1:
        pairContestants = []
        potentialCoords = pairCoords(x, y)
        for x2, y2 in potentialCoords:
          if 0 <= x2 < board.width and 0 <= y2 < board.height:
            cell2 = board.grid[y2][x2]
            numMines2 = board.cellMinesNum(cell2)
            numFlags2 = board.cellFlagsNum(cell2)
            if cell2.isVisible and numMines2 > 0 and numFlags2 != numMines2:
              pairContestants.append((cell2, numMines2, numFlags2))
        for cell2, numMines2, numFlags2 in pairContestants:
          set1 = {neighbor for neighbor in board.neighbors(cell) if not neighbor.isFlagged and not neighbor.isVisible}
          set1MineCount = numMines1 - numFlags1
          set2 = {neighbor for neighbor in board.neighbors(cell2) if not neighbor.isFlagged and not neighbor.isVisible}
          set2MineCount = numMines2 - numFlags2
          biggerSet, biggerSetMineCount = (set1, set1MineCount) if len(set1) > len(set2) else (set2, set2MineCount)
          smallerSet, smallerSetMineCount = (set2, set2MineCount) if len(set1) > len(set2) else (set1, set1MineCount)
          intersection = set1.intersection(set2)
          if intersection == smallerSet:
            reducedSet = biggerSet - smallerSet
            reducedSetMineCount = smallerSetMineCount
            if len(reducedSet) == reducedSetMineCount and len(reducedSet) > 0:
              print(f"Found set intersection at ({x}, {y}) and ({cell2.location[0]}, {cell2.location[1]})")
              return FlagCells({neighbor.location for neighbor in reducedSet})
  return None

def getSetIntersectionRevealMove(board: Board) -> FlagCells:
  """
  Attempts to find a pair of cells where the intersection of their neighbors reveals safe cells.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    RevealCells: The move to reveal the cells, or None if no move is found.
  """
  # TODO: Implement this move

def getRemainingMinesFlagMove(board: Board) -> FlagCells:
  """
  Attempts to find a set of cells that can be flagged as mines based on the number of remaining mines on the board.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    FlagCells: The move to flag the cells, or None if no move is found.
  """
  # TODO: Implement this move
  pass

def getRemainingCellRevealsMove(board: Board) -> ExpandCell:
  """
  Attempts to find a set of cells that can be safely revealed based on the number of remaining mines on the board.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    RevealCell: The move to reveal the cells, or None if no move is found.
  """
  # TODO: Implement this move
  pass

def getNextMove(board: Board) -> Move:
  """
  Determines the next move to make on the Minesweeper board.
  Args:
    board (Board): The Minesweeper board.
  Returns:
    Move: The move to make, or None if no move is found.
  """
  order = [
    getRevealCellMove,
    getExpandCellMove,
    getFlagRemainingCellMove,
    getSetIntersectionFlagMove,
    getRemainingMinesFlagMove,
    getRemainingCellRevealsMove
  ]
  for moveFunction in order:
    move = moveFunction(board)
    if move:
      return move
  return None