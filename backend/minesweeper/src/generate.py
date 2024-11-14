import random
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.solver import getNextMove
from src.classes.Board import Board
from src.classes.Cell import Cell

def basicGrid(width: int, height: int, mines: int, startLocation: tuple[int, int]) -> list[list[Cell]]:
  """
  Generate a basic board with mines placed randomly.

  Args:
    startLocation (tuple[int, int]): The starting location on the board.

  Returns:
    list[list[Cell]]: The generated board.
  """
  # print("Generating normal board...")
  newBoard = [[Cell(False, False, False, (x, y)) for x in range(width)] for y in range(height)]
  startingSquareLocations: tuple[int, int] = []
  remainingSquareLocations: tuple[int, int] = []
  for y in range(height):
    for x in range(width):
      if abs(x - startLocation[0]) <= 1 and abs(y - startLocation[1]) <= 1:
        startingSquareLocations.append((x, y))
      else:
        remainingSquareLocations.append((x, y))
  # print(f"Square locations: {len(remainingSquareLocations)}")
  remainingMines = mines
  for y in range(height):
    for x in range(width):
      if (x, y) in startingSquareLocations:
        newBoard[y][x].isMine = False
      else:
        newBoard[y][x].isMine = random.random() < remainingMines / len(remainingSquareLocations)
        if newBoard[y][x].isMine:
          remainingMines -= 1
          # print(f"Remaining mines: {remainingMines}")
        remainingSquareLocations.remove((x, y))
  return newBoard

def generateBoard(width: int, height: int, mines: int, startLocation: tuple[int, int]) -> Board:
  """
  Generate a board with mines placed randomly, ensuring the start location is safe.

  Args:
    startLocation (tuple[int, int]): The starting location on the board.

  Raises:
    ValueError: If the start location is out of bounds.
  """
  if (startLocation[0] < 0 or startLocation[0] >= width) or (startLocation[1] < 0 or startLocation[1] >= height):
    raise ValueError("Start location is out of bounds")
  grid = basicGrid(width, height, mines, startLocation)
  board = Board(width=width, height=height, mines=mines, startLocation=startLocation, grid=grid)
  board.revealCell(board.grid[startLocation[1]][startLocation[0]])
  solved = False
  completeRestarts = 0
  while not solved and completeRestarts < 10:
    board.display()
    nextMove = getNextMove(board)
    if nextMove is None:
      concurrentShuffles = 0
      while concurrentShuffles < 10 and getNextMove(board) is None:
        board.shuffleRemainingMines()
        concurrentShuffles += 1
      if concurrentShuffles >= 10:
        newGrid = basicGrid(width, height, mines, startLocation)
        board.grid = newGrid
        board.revealCell(board.grid[startLocation[1]][startLocation[0]])
        completeRestarts += 1
    else:
      for x, y in nextMove.cellsToReveal:
        board.revealCell(board.grid[y][x])
      for x, y in nextMove.cellsToFlag:
        board.flagCell(board.grid[y][x])
      for x, y in nextMove.cellsToExpand:
        board.revealCell(board.grid[y][x])
    if board.isSolved():
      solved = True
  if completeRestarts >= 10:
    raise ValueError("Could not generate a solvable board")
  # hide everything but the start location
  for y in range(height):
    for x in range(width):
      board.grid[y][x].isVisible = False
  board.revealCell(board.grid[startLocation[1]][startLocation[0]])
  return board

testBoard = generateBoard(5, 5, 5, (0, 0))
testBoard.display(True)
