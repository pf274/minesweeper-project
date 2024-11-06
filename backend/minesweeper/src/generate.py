import random
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.classes.Board import Board
from src.classes.Cell import Cell

def basicBoard(width: int, height: int, mines: int, startLocation: tuple[int, int]) -> list[list[Cell]]:
  """
  Generate a basic board with mines placed randomly.

  Args:
    startLocation (tuple[int, int]): The starting location on the board.

  Returns:
    list[list[Cell]]: The generated board.
  """
  print("Generating insoluble board...")
  newBoard = [[Cell(False, False, False, (x, y)) for x in range(width)] for y in range(height)]
  startingSquareLocations: tuple[int, int] = []
  remainingSquareLocations: tuple[int, int] = []
  for y in range(height):
    for x in range(width):
      if abs(x - startLocation[0]) <= 1 and abs(y - startLocation[1]) <= 1:
        startingSquareLocations.append((x, y))
      else:
        remainingSquareLocations.append((x, y))
  print(f"Square locations: {len(remainingSquareLocations)}")
  remainingMines = mines
  for y in range(height):
    for x in range(width):
      if (x, y) in startingSquareLocations:
        newBoard[y][x].isMine = False
      else:
        newBoard[y][x].isMine = random.random() < remainingMines / len(remainingSquareLocations)
        if newBoard[y][x].isMine:
          remainingMines -= 1
          print(f"Remaining mines: {remainingMines}")
        remainingSquareLocations.remove((x, y))
  return newBoard

def generateBoard(width: int, height: int, mines: int, startLocation: tuple[int, int]) -> list[list[Cell]]:
  """
  Generate a board with mines placed randomly, ensuring the start location is safe.

  Args:
    startLocation (tuple[int, int]): The starting location on the board.

  Raises:
    ValueError: If the start location is out of bounds.
  """
  if (startLocation[0] < 0 or startLocation[0] >= width) or (startLocation[1] < 0 or startLocation[1] >= height):
    raise ValueError("Start location is out of bounds")
  print("Generating soluble board...")
  basicBoard(width, height, mines, startLocation)
  # TODO: generate complex board