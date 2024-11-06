from typing import Literal
import random
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.classes.Cell import Cell

class Board:
	def __init__(self, *, width: int, height: int, mines: int, startLocation: tuple[int, int] = (None, None), grid: list[list[Cell]] = None):
		"""
		Initialize the Board.

		Args:
			width (int): The width of the board.
			height (int): The height of the board.
			mines (int): The number of mines on the board.
			startLocation (tuple[int, int], optional): The starting location on the board. Defaults to (None, None).
			grid (list[list[Cell]], optional): The grid of cells. Defaults to None.

		You must provide either a grid or a start location to generate the board.

		Raises:
			ValueError: If required parameters are missing or start location is not provided when grid is None.
		"""
		self.width = width
		self.height = height
		self.mines = mines
		requiredParams = ['width', 'height', 'mines']
		missingParams = [param for param in requiredParams if self.__dict__[param] is None]
		if missingParams:
			raise ValueError(f"Missing required parameters: {', '.join(missingParams)}")
		if grid is None:
			if startLocation[0] is None or startLocation[1] is None:
				raise ValueError("Start location must be provided if grid is not provided")
			self.generateBoard(startLocation)
		else:
			self.grid = grid

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

	def display(self):
		"""
		Display the board in the console.
		"""
		print("+" + "-" * self.width * 2 + "+")
		for row in self.grid:
			print("|", end="")
			for cell in row:
				if cell.isVisible:
					if cell.isMine:
						print("����", end=" ")
					else:
						print(self.cellMinesNum(cell), end=" ")
				elif cell.isFlagged:
					print("⚑", end=" ")
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
			number = self.cellMinesNum(cell)
			flaggedNeighbors = sum(1 for neighbor in neighbors if neighbor.isFlagged)
			neighborsSafe = True
			if number == flaggedNeighbors:
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

	def basicBoard(self, startLocation: tuple[int, int]) -> list[list[Cell]]:
		"""
		Generate a basic board with mines placed randomly.

		Args:
			startLocation (tuple[int, int]): The starting location on the board.

		Returns:
			list[list[Cell]]: The generated board.
		"""
		print("Generating insoluble board...")
		newBoard = [[Cell(False, False, False, (x, y)) for x in range(self.width)] for y in range(self.height)]
		startingSquareLocations: tuple[int, int] = []
		remainingSquareLocations: tuple[int, int] = []
		for y in range(self.height):
			for x in range(self.width):
				if abs(x - startLocation[0]) <= 1 and abs(y - startLocation[1]) <= 1:
					startingSquareLocations.append((x, y))
				else:
					remainingSquareLocations.append((x, y))
		print(f"Square locations: {len(remainingSquareLocations)}")
		remainingMines = self.mines
		for y in range(self.height):
			for x in range(self.width):
				if (x, y) in startingSquareLocations:
					newBoard[y][x].isMine = False
				else:
					newBoard[y][x].isMine = random.random() < remainingMines / len(remainingSquareLocations)
					if newBoard[y][x].isMine:
						remainingMines -= 1
						print(f"Remaining mines: {remainingMines}")
					remainingSquareLocations.remove((x, y))
		self.grid = newBoard

	def generateBoard(self, startLocation: tuple[int, int]):
		"""
		Generate a board with mines placed randomly, ensuring the start location is safe.

		Args:
			startLocation (tuple[int, int]): The starting location on the board.

		Raises:
			ValueError: If the start location is out of bounds.
		"""
		if (startLocation[0] < 0 or startLocation[0] >= self.width) or (startLocation[1] < 0 or startLocation[1] >= self.height):
			raise ValueError("Start location is out of bounds")
		print("Generating soluble board...")
		self.basicBoard(startLocation)
		# TODO 2: generate complex board

	def getNextStep(self) -> tuple[Literal['reveal', 'flag'], set[tuple[int, int]]]:
		"""
		Determine the next step for the solver.

		Returns:
			tuple[Literal['reveal', 'flag'], set[tuple[int, int]]]: The next action and the set of cells to act on.
		"""
		# TODO 1: implement solver!
		return ('reveal', {(0, 0)})

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
			"mines": self.mines
		}

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
		grid = [[Cell(cell['isMine'], cell['isVisible'], cell['isFlagged'], cell['location']) for cell in row] for row in grid]
		return Board(width=width, height=height, mines=mines, grid=grid)
	except:
		print("Could not parse board JSON")
		return None