from typing import Literal
import random
import json

class Cell:
    def __init__(self, isMine: bool, isVisible: bool, isFlagged: bool, location: tuple[int, int]):
        self.isMine = isMine
        self.isVisible = isVisible
        self.isFlagged = isFlagged
        self.location = location
    def neighbors(self) -> list[tuple[int, int]]:
        x, y = self.location
        neighborLocations = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        neighbors = []
        for dx, dy in neighborLocations:
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                neighbors.append((x + dx, y + dy))
        return neighbors
    def toJSON(self):
        return {
            "isMine": self.isMine,
            "isVisible": self.isVisible,
            "isFlagged": self.isFlagged,
            "location": self.location
        }

class Board:
    def __init__(self, *, width: int, height: int, mines: int, startLocation: tuple[int, int] = (None, None), grid: list[list[Cell]] = None):
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

    def getNextStep(self) -> tuple[Literal['reveal', 'flag'], tuple[int, int]]:
        # TODO 1: implement solver!
        return ('reveal', (0, 0))
    def basicBoard(self, startLocation: tuple[int, int]) -> list[list[Cell]]:
        newBoard = [[Cell(False, False, False, (x, y)) for x in range(self.width)] for y in range(self.height)]
        startingSquareLocations: tuple[int, int] = []
        remainingSquareLocations: tuple[int, int] = []
        for y in range(self.height):
            for x in range(self.width):
                if abs(x - startLocation[0]) <= 1 and abs(y - startLocation[1]) <= 1:
                    startingSquareLocations.append((x, y))
                else:
                    remainingSquareLocations.append((x, y))
        remainingMines = self.mines
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in startingSquareLocations:
                    newBoard[y][x].isMine = False
                else:
                    newBoard[y][x].isMine = random.random() < remainingMines / len(remainingSquareLocations)
                    if newBoard[y][x].isMine:
                        remainingMines -= 1
        return newBoard
    def generateBoard(self, startLocation: tuple[int, int]):
        base = self.basicBoard(startLocation)
        # TODO 2: generate complex board
        self.grid = base
    def toJSON(self):
        return {
            "grid": [[cell.toJSON() for cell in row] for row in self.grid],
            "width": self.width,
            "height": self.height,
            "mines": self.mines
        }

def parseBoard(boardJson: json) -> Board:
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
