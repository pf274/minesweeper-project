import json
from Board import parseBoard
from generate import generateBoard
from solver import getNextMove
# Board generation route: https://06koy0jra2.execute-api.us-east-1.amazonaws.com/genboard
# Hint Provider route: https://06koy0jra2.execute-api.us-east-1.amazonaws.com/hint

def handler(event: dict, context: dict) -> dict:
  """
  Handles incoming HTTP requests for the Minesweeper backend.
  Args:
    event (dict): The event dictionary containing request data.
      - requestContext (dict): Contains HTTP request information such as path and method.
      - body (str): The JSON string body of the request.
      - queryStringParameters (dict): The query string parameters of the request.
    context (dict): The context dictionary (not used in this handler).
  Returns:
    dict: The response dictionary with status code and body.
  The handler processes the following paths and methods:
    - GET /genboard: Generates a new Minesweeper board.
    - POST /hint: Provides a hint for the Minesweeper game.
    - Returns a 400 status code for invalid paths or methods.
    - Returns a 500 status code for internal server errors.
  """
  print(event)

  # get input data
  path = event['requestContext']['http']['path']
  method = event['requestContext']['http']['method']
  inBody = None
  if 'body' in event:
    inBody = event['body']
  try:
    if inBody is not None:
      inBody = json.loads(event['body'])
  except:
    print("Could not parse body as JSON")
  event['body'] = inBody
  queryStringParameters = dict()
  if 'queryStringParameters' in event and event['queryStringParameters'] is not None:
    queryStringParameters = event['queryStringParameters']
  print(f"Path: {path}, Method: {method}, Body: {inBody}, Query: {queryStringParameters}")
  # handle request
  try:
    if "genboard" in path and method == "GET":
      return handle_genboard(queryStringParameters)
    elif 'hint' in path and method == "POST":
      return handle_hint(inBody)
    else:
      return generate_response(400, {"message": "Invalid path or method"})
  except Exception as e:
    return generate_response(500, {"message": str(e)})

def handle_genboard(params: dict) -> dict:
  """
  Handles the generation of a Minesweeper board based on the provided parameters.
  Args:
    params (dict): A dictionary containing the following keys:
      - 'width' (str): The width of the board.
      - 'height' (str): The height of the board.
      - 'mines' (str): The number of mines to place on the board.
      - 'startX' (str): The starting X coordinate.
      - 'startY' (str): The starting Y coordinate.
  Returns:
    dict: A dictionary representing the HTTP response. If successful, the response contains
        a message and the generated board in JSON format. If any required parameter is missing
        or invalid, the response contains an error message.
  """

  requiredParams = ['width', 'height', 'mines', 'startX', 'startY']
  for param in requiredParams:
    if param not in params:
      return generate_response(400, {"message": f"Missing query parameter: {param}"})
    if not params[param].isdigit():
      return generate_response(400, {"message": f"Invalid query parameter: {param}"})
  
  width = int(params['width'])
  height = int(params['height'])
  mines = int(params['mines'])
  startX = int(params['startX'])
  startY = int(params['startY'])
  boardInst = generateBoard(width, height, mines, (startX, startY))
  boardInst.display()
  outBody = {
    "message": f"Generated board with width: {width}, height: {height}, mines: {mines}",
    "board": boardInst.toJSON()
  }
  return generate_response(200, outBody)

def handle_hint(body: dict) -> dict:
  """
  Handles the request to provide a hint for the Minesweeper game.

  Args:
    body (dict): A dictionary containing the board state.
  Returns:
    dict: A response dictionary containing the status code and either a hint or an error message.
  The function performs the following steps:
  1. Parses the board from the provided body.
  2. If the board format is invalid, returns a 400 response with an error message.
  3. If the board format is valid, retrieves a hint from the parsed board.
  4. Returns a 200 response with the hint.
  """
  parsedBoard = parseBoard(body)
  if parsedBoard is None:
    return generate_response(400, {"message": "Invalid board format"})
  move = getNextMove(parsedBoard)
  hint = [hintStep.toJSON() for hintStep in move.hintSteps]
  return generate_response(200, {"hint": hint})

def generate_response(statusCode: int, body: dict) -> dict:
  """
  Generates an HTTP response dictionary.
  Args:
    statusCode (int): The HTTP status code for the response.
    body (dict): The body of the response, which will be JSON-encoded.
  Returns:
    dict: A dictionary representing the HTTP response with keys 'statusCode' and 'body'.
  """
  return {"statusCode": statusCode, "body": json.dumps(body)}