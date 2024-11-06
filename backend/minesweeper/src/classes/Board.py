from typing import Literal
import random
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.classes.Cell import Cell

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
		self.mines = mines
		self.grid = grid
		self.startLocation = startLocation
		requiredParams = ['width', 'height', 'mines', 'startLocation', 'grid']
		missingParams = [param for param in requiredParams if self.__dict__[param] is None]
		if missingParams:
			raise ValueError(f"Missing required parameters: {', '.join(missingParams)}")

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