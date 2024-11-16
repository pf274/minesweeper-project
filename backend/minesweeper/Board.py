import itertools
import random
import json
from Cell import Cell

class Board:
  def __init__(self, *, width: int, height: int, mines: int, startLocation: tuple[int, int], grid: list[list[Cell]]):
    """
    Initialize the Board.

    Args:
      width (int): The width of the board.
      height (int): The height of the board.
      mines (int): The number of mines on the board.
      startLocation tuple[int, int]: The starting location on the board
      grid list[list[Cell]]: The grid of cells

    Raises:
      ValueError: If required parameters are missing or start location is not provided when grid is None.
    """
    self.width = width
    self.height = height
    self.grid = grid
    self.mines = self.getMineCount()
    self.startLocation = startLocation
    requiredParams = ['width', 'height', 'mines', 'startLocation', 'grid']
    missingParams = [param for param in requiredParams if self.__dict__[param] is None]
    if missingParams:
      raise ValueError(f"Missing required parameters: {', '.join(missingParams)}")
		
  def getMineCount(self) -> int:
    """
    Get the number of mines on the board.

    Returns:
      int: The number of mines.
    """
    return sum(1 for row in self.grid for cell in row if cell.isMine)

  def getRemainingMineCount(self) -> int:
    """
    Get the number of remaining mines on the board.

    Returns:
      int: The number of remaining mines.
    """
    return self.mines - sum(1 for row in self.grid for cell in row if cell.isFlagged)
	
  def shuffleRemainingMines(self, returnAll: bool = False) -> list[list[Cell]]:
    """
    Shuffle the remaining mines on the board.
    """
    remainingSquares = [(x, y) for y in range(self.height) for x in range(self.width) if not self.grid[y][x].isVisible and not self.grid[y][x].isFlagged]
    currentMineLayout = set([(x, y) for y in range(self.height) for x in range(self.width) if self.grid[y][x].isMine and not self.grid[y][x].isFlagged])
    numRemainingMines = self.getRemainingMineCount()
    combinations = []
    for combination in itertools.combinations(remainingSquares, numRemainingMines):
      combinations.append(set(combination))
      if len(combinations) >= 10:
        break
    if currentMineLayout in combinations:
      try:
        combinations.remove(currentMineLayout)
      except:
        print("Current mine layout not in combinations")
    if returnAll:
      newGrids = []
      for combination in combinations:
        gridCopy = [[Cell(cell.isMine, cell.isVisible, cell.isFlagged, cell.location) for cell in row] for row in self.grid]
        for x, y in remainingSquares:
          if (x, y) in combination:
            gridCopy[y][x].isMine = True
          else:
            gridCopy[y][x].isMine = False
        newGrids.append(gridCopy)
      return newGrids
    if len(combinations) == 0:
      return None
    combination = random.choice(combinations)
    for x, y in remainingSquares:
      if (x, y) in combination:
        self.grid[y][x].isMine = True
      else:
        self.grid[y][x].isMine = False
    return self.grid


  def neighbors(self, cell: Cell) -> list[Cell]:
    """
    Get the neighboring cells of a given cell.

    Args:
        cell (Cell): The cell for which to find the neighbors.

    Returns:
        list[Cell]: A list of neighboring cells.
    """
    x, y = cell.location
    neighborLocations = [
      (-1, -1), (0, -1), (1, -1),
      (-1, 0), (1, 0),
      (-1, 1), (0, 1), (1, 1)
    ]
    neighbors = []
    for dx, dy in neighborLocations:
      if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
        neighbors.append(self.grid[y + dy][x + dx])
    return neighbors

  def cellMinesNum(self, cell: Cell) -> int:
    """
    Get the number of mines around a given cell.

    Args:
      cell (Cell): The cell for which to count neighboring mines.

    Returns:
      int: The number of neighboring mines.
    """
    neighbors = self.neighbors(cell)
    return sum(1 for neighbor in neighbors if neighbor.isMine)

  def cellFlagsNum(self, cell: Cell) -> int:
    """
    Get the number of flags around a given cell.

    Args:
      cell (Cell): The cell for which to count neighboring flags.

    Returns:
      int: The number of neighboring flags.
    """
    neighbors = self.neighbors(cell)
    return sum(1 for neighbor in neighbors if neighbor.isFlagged)

  def display(self, revealed: bool = False):
    """
    Display the board in the console.
    """
    print("+" + "-" * self.width * 2 + "+")
    for row in self.grid:
      print("|", end="")
      for cell in row:
        if cell.isVisible or revealed:
          if cell.isMine:
            print("!", end=" ")
          else:
            print(self.cellMinesNum(cell), end=" ")
        elif cell.isFlagged:
          print("F", end=" ") # ⚑
        else:
          print("?", end=" ")
      print("|")
    print("+" + "-" * self.width * 2 + "+")

  def revealCell(self, cell: Cell) -> bool:
    """
    Reveal a cell and its neighbors if necessary.

    Args:
      cell (Cell): The cell to reveal.

    Returns:
      bool: True if the cell is not a mine, False otherwise.
    """
    if cell.isVisible:  # reveal neighbors if all mines are flagged
      neighbors = self.neighbors(cell)
      numberOfMines = self.cellMinesNum(cell)
      numberOfFlags = self.cellFlagsNum(cell)
      neighborsSafe = True
      if numberOfMines == numberOfFlags:
        for neighbor in neighbors:
          if not neighbor.isVisible and not neighbor.isFlagged:
            neighborsSafe = self.revealCell(neighbor) and neighborsSafe
      return neighborsSafe
    else:  # reveal cells recursively
      cell.isVisible = True
      if self.cellMinesNum(cell) == 0:
        for neighbor in self.neighbors(cell):
          self.revealCell(neighbor)
      return not cell.isMine

  def flagCell(self, cell: Cell):
    """
    Toggle the flag status of a cell.

    Args:
      cell (Cell): The cell to flag or unflag.
    """
    cell.isFlagged = not cell.isFlagged

  def toJSON(self):
    """
    Convert the board to a JSON-serializable dictionary.

    Returns:
      dict: The JSON-serializable representation of the board.
    """
    return {
      "grid": [[cell.toJSON() for cell in row] for row in self.grid],
      "width": self.width,
      "height": self.height,
      "mines": self.mines,
      "startX": self.startLocation[0],
      "startY": self.startLocation[1]
    }
  def isSolved(self):
    """
    Check if the board is solved.

    Returns:
      bool: True if the board is solved, False otherwise.
    """
    for row in self.grid:
      for cell in row:
        if cell.isVisible and cell.isMine:
          return False
        if not cell.isVisible and not cell.isMine:
          return False
    return True

def parseBoard(boardJson: json) -> Board:
	"""
	Parse a JSON representation of a board into a Board object.

	Args:
		boardJson (json): The JSON representation of the board.

	Returns:
		Board: The parsed Board object, or None if parsing fails.
	"""
	try:
		grid = boardJson['grid']
		width = boardJson['width']
		height = boardJson['height']
		mines = boardJson['mines']
		startX = boardJson['startX']
		startY = boardJson['startY']
		grid = [[Cell(cell['isMine'], cell['isVisible'], cell['isFlagged'], (cell['location'][0], cell['location'][1])) for cell in row] for row in grid]
		return Board(width=width, height=height, mines=mines, grid=grid, startLocation=(startX, startY))
	except Exception as e:
		print("Could not parse board JSON" + str(e))
		return None
	
def boardFromString(boardString: str) -> Board:
	"""
	Generate a Board object from a string.

	Args:
		boardString (str): The string representation of the board.

	Returns:
		Board: The Board object, or None if parsing fails.
	"""
	try:
		lines = [line.strip() for line in boardString.split("\n") if line.strip() != '' and line.strip() != '\n']
		width = len(lines[0])
		height = len(lines)
		numMines = boardString.count('M') + boardString.count('F')
		grid = [[Cell(False, True, False, (x, y)) for x in range(width)] for y in range(height)]
		for y, line in enumerate(lines):
			for x, char in enumerate(line):
				if char == 'M':
					grid[y][x].isMine = True
					grid[y][x].isFlagged = False
					grid[y][x].isVisible = False
				elif char == 'F':
					grid[y][x].isFlagged = True
					grid[y][x].isMine = True
					grid[y][x].isVisible = False
				elif char == '?':
					grid[y][x].isVisible = False
					grid[y][x].isMine = False
					grid[y][x].isFlagged = False
				elif char == '.':
					grid[y][x].isVisible = True
					grid[y][x].isMine = False
					grid[y][x].isFlagged = False
				else:
					raise ValueError(f"Invalid character: {char}")
		boardInst = Board(width=width,height=height,mines=numMines, grid=grid, startLocation=(0, 0))
		return boardInst
	except Exception as e:
		print(f"Could not parse board string: {e}")
		return None