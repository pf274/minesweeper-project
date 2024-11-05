import json
import random
# https://06koy0jra2.execute-api.us-east-1.amazonaws.com/genboard
# https://06koy0jra2.execute-api.us-east-1.amazonaws.com/hint
debugging = False

def handler(event: dict, context: dict) -> dict:
    # get input data
    path = event['requestContext']['http']['path']
    method = event['requestContext']['http']['method']
    inBody = event['body']
    try:
        inBody = json.loads(event['body'])
    except:
        print("Could not parse body as JSON")
    event['body'] = inBody
    queryStringParameters = event['queryStringParameters']
    if queryStringParameters is None:
        queryStringParameters = {}
    print(queryStringParameters)
    # TODO: reroute
    outBody = {}
    if "genboard" in path and method == "GET":
        requiredParams = ['width', 'height', 'mines', 'startX', 'startY']
        for param in requiredParams:
            if param not in queryStringParameters:
                outBody = {
                    "message": f"Missing query parameter: {param}"
                }
                response = {"statusCode": 400, "body": json.dumps(outBody)}
                return response
            if not queryStringParameters[param].isdigit():
                outBody = {
                    "message": f"Invalid query parameter: {param}"
                }
                response = {"statusCode": 400, "body": json.dumps(outBody)}
                return response
        width = int(queryStringParameters['width'])
        height = int(queryStringParameters['height'])
        mines = int(queryStringParameters['mines'])
        startX = int(queryStringParameters['startX'])
        startY = int(queryStringParameters['startY'])
        boardInst = Board(width=width, height=height, mines=mines, startLocation=(startX, startY))
        outBody = {
            "message": f"Generating board with width: {width}, height: {height}, mines: {mines}",
            "board": boardInst
        }
    elif 'hint' in path and method == "POST":
        parsedBoard = parseBoard(inBody)
        if parsedBoard is None:
            outBody = {
                "message": "Invalid board format"
            }
            response = {"statusCode": 400, "body": json.dumps(outBody)}
            return response
        else:
            hint = parsedBoard.getHint()
            outBody = {
                "hint": hint
            }
    else:
        outBody = {
            "message": "Invalid path or method"
        }
        response = {"statusCode": 400, "body": json.dumps(outBody)}
        return response
    # return response

    response = {"statusCode": 200, "body": json.dumps(outBody)}

    return response

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

class Board:
    def __init__(self, *, width: int, height: int, mines: int, startLocation: tuple[int, int] = (None, None), board: list[list[Cell]] = None):
        self.width = width
        self.height = height
        self.mines = mines
        requiredParams = ['width', 'height', 'mines']
        missingParams = [param for param in requiredParams if self.__dict__[param] is None]
        if missingParams:
            raise ValueError(f"Missing required parameters: {', '.join(missingParams)}")
        if board is None:
            if startLocation[0] is None or startLocation[1] is None:
                raise ValueError("Start location must be provided if board is not provided")
            self.generateBoard(startLocation)
        else:
            self.grid = board

    def getHint(self):
        return getNextStep(self)
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
        # TODO: generate complex board
        self.grid = base

def parseBoard(board: json) -> Board:
    # TODO: parse board
    return None

from typing import Literal

def getNextStep(board: Board) -> tuple[Literal['reveal', 'flag'], tuple[int, int]]:
    # TODO: implement solver!
    return ('reveal', (0, 0))

if debugging:
    print(handler({}, {}))