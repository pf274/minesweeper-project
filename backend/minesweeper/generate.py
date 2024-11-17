import math
import random
from solver import getNextMove
from Board import Board
from Cell import Cell

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
  x, y = startLocation
  if (x < 0 or x >= width) or (y < 0 or y >= height):
    raise ValueError("Start location is out of bounds")
  grid = basicGrid(width, height, mines, startLocation)
  board = Board(width=width, height=height, mines=mines, startLocation=startLocation, grid=grid)
  board.revealCell(board.grid[y][x])
  solved = False
  completeRestarts = 0
  levels = [board.copy()]
  while not solved and completeRestarts < 5:
    nextMove = getNextMove(board)
    if nextMove is None:
      concurrentShuffles = 0
      while concurrentShuffles < 10 and nextMove is None:
        board.shuffleRemainingMines()
        concurrentShuffles += 1
        nextMove = getNextMove(board)
        if nextMove is not None:
          levels.append(board.copy())
      if concurrentShuffles >= 10:
        if len(levels) == 0:
          newGrid = basicGrid(width, height, mines, startLocation)
          board.grid = newGrid
          board.revealCell(board.grid[y][x])
          levels.append(board.copy())
          completeRestarts += 1
        else:
          board = levels.pop()
    else:
      for x2, y2 in nextMove.cellsToReveal:
        board.revealCell(board.grid[y2][x2])
      for x2, y2 in nextMove.cellsToFlag:
        board.flagCell(board.grid[y2][x2])
      for x2, y2 in nextMove.cellsToExpand:
        board.revealCell(board.grid[y2][x2])
    if board.isSolved():
      solved = True
  if completeRestarts >= 10:
    raise ValueError("Could not generate a solvable board")
  # hide everything but the start location
  for y2 in range(height):
    for x2 in range(width):
      board.grid[y2][x2].isVisible = False
      board.grid[y2][x2].isFlagged = False
  board.revealCell(board.grid[y][x])
  return board

def perturbBoard(board: Board):
  """
  Perturb the board by either moving a mine from the frontier to another unrevealed cell or into the revealed area.
  """
  startingCell = board.grid[board.startLocation[1]][board.startLocation[0]]
  startingCells = {startingCell.location}
  startingNeighbors = board.neighbors(startingCell)
  for neighbor in startingNeighbors:
    startingCells.add(neighbor.location)
  visibleCells = set()
  unflaggedMinesInFrontier = set()
  flaggedMinesInFrontier = set()
  hiddenCellsNotInFrontier = set() # unrevealed cells not adjacent to revealed cells (not mines)
  for y in range(board.height):
    for x in range(board.width):
      cell = board.grid[y][x]
      if not cell.isVisible:
        cellNeighbors = board.neighbors(cell)
        hasVisibleNeighbor = any(neighbor.isVisible for neighbor in cellNeighbors)
        if hasVisibleNeighbor:
          numRevealedOrdinalNeighbors = len({neighbor for neighbor in cellNeighbors if sum(abs(neighbor.location[i] - cell.location[i]) for i in range(2)) == 1 and neighbor.isVisible})
          if numRevealedOrdinalNeighbors < 3:
            if cell.isMine:
              if cell.isFlagged:
                flaggedMinesInFrontier.add(cell)
              else:
                unflaggedMinesInFrontier.add(cell)
          elif not cell.isMine:
            hiddenCellsNotInFrontier.add(cell)
        elif not cell.isMine:
          hiddenCellsNotInFrontier.add(cell)
      elif cell.location not in startingCells:
        visibleCells.add(cell)
  sourceCell = None
  targetCell = None
  if len(unflaggedMinesInFrontier) > 0: # move the mine to a random hidden cell
    sourceCell = random.choice(list(unflaggedMinesInFrontier))
  elif len(flaggedMinesInFrontier) > 0: # move the mine to a random hidden cell
    sourceCell = random.choice(list(flaggedMinesInFrontier))
  else:
    raise ValueError("No mines in frontier")
  if len(hiddenCellsNotInFrontier) > 0:
    targetCell = random.choice(list(hiddenCellsNotInFrontier))
  elif len(visibleCells) > 0:
    targetCell = random.choice(list(visibleCells))
  else:
    raise ValueError("No hidden cells or visible cells to move mine to")
  # print(f"Moved mine from {sourceCell.location} to {targetCell.location}")
  sourceCell.isMine = False
  sourceCell.isFlagged = False
  sourceCell.isVisible = False
  targetCell.isMine = True
  targetCell.isFlagged = False
  targetCell.isVisible = False

def generateBoard2(width: int, height: int, mines: int, startLocation: tuple[int, int]) -> Board:
  """
  Generate a board with mines placed randomly, ensuring the start location is safe.

  Args:
    startLocation (tuple[int, int]): The starting location on the board.

  Raises:
    ValueError: If the start location is out of bounds.
  """
  x, y = startLocation
  if (x < 0 or x >= width) or (y < 0 or y >= height):
    raise ValueError("Start location is out of bounds")
  grid = basicGrid(width, height, mines, startLocation)
  board = Board(width=width, height=height, mines=mines, startLocation=startLocation, grid=grid)
  def reshuffleBoard():
    newGrid = basicGrid(width, height, mines, startLocation)
    board.grid = newGrid
    board.revealCell(board.grid[y][x])
  def resetBoard():
    for row in board.grid:
      for cell in row:
        cell.isVisible = False
        cell.isFlagged = False
    board.revealCell(board.grid[y][x])
  board.revealCell(board.grid[y][x])
  solved = False
  boardRevealed = False
  prevNumPerturbations = math.inf
  perturbations = 0
  iterations = 0
  while not solved:
    while perturbations < prevNumPerturbations and not solved:
      nextMove = getNextMove(board)
      while not boardRevealed and perturbations < prevNumPerturbations:
        if nextMove is None:
          if board.isSolved():
            if perturbations == 0:
              print(f"Iteration {iterations}: {perturbations}")
              solved = True
            boardRevealed = True
            break
          else:
            perturbBoard(board)
            perturbations += 1
        else:
          for x2, y2 in nextMove.cellsToReveal:
            if board.grid[y2][x2].isMine:
              print(f"Revealed mine at {x2}, {y2}")
              raise ValueError("Revealed mine")
            board.revealCell(board.grid[y2][x2])
          for x2, y2 in nextMove.cellsToFlag:
            if not board.grid[y2][x2].isMine:
              print(f"Flagged safe square at {x2}, {y2}")
              raise ValueError("Flagged safe square")
            board.flagCell(board.grid[y2][x2])
          for x2, y2 in nextMove.cellsToExpand:
            if board.grid[y2][x2].isMine:
              print(f"Revealed mine at {x2}, {y2}")
              raise ValueError("Revealed mine")
            board.revealCell(board.grid[y2][x2])
        nextMove = getNextMove(board)
      if boardRevealed and not solved:
        print(f"Iteration {iterations}: {perturbations}")
        # print(f"Perturbations: {perturbations} vs. {prevNumPerturbations}")
        resetBoard()
        boardRevealed = False
        prevNumPerturbations = perturbations
        perturbations = 0
        iterations += 1
    if not solved:
      print("Took more perturbations than before")
      print(f"Restarting...")
      prevNumPerturbations = math.inf
      perturbations = 0
      reshuffleBoard()
  resetBoard()
  return board
  


# testBoard = generateBoard2(30, 16, 179, (4, 4))
# testBoard.display(True)
# testBoard.display(False)
