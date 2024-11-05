import json
from solver import Board, parseBoard
# Board generation route: https://06koy0jra2.execute-api.us-east-1.amazonaws.com/genboard
# Hint Provider route: https://06koy0jra2.execute-api.us-east-1.amazonaws.com/hint

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
    queryStringParameters = event['queryStringParameters'] or {}
    # handle request
    if "genboard" in path and method == "GET":
        return handle_genboard(queryStringParameters)
    elif 'hint' in path and method == "POST":
        return handle_hint(inBody)
    else:
        return generate_response(400, {"message": "Invalid path or method"})

def handle_genboard(params: dict) -> dict:
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
    boardInst = Board(width=width, height=height, mines=mines, startLocation=(startX, startY))
    outBody = {
        "message": f"Generating board with width: {width}, height: {height}, mines: {mines}",
        "board": boardInst
    }
    return generate_response(200, outBody)

def handle_hint(body: dict) -> dict:
    parsedBoard = parseBoard(body)
    if parsedBoard is None:
        return generate_response(400, {"message": "Invalid board format"})
    hint = parsedBoard.getHint()
    return generate_response(200, {"hint": hint})

def generate_response(statusCode: int, body: dict) -> dict:
    return {"statusCode": statusCode, "body": json.dumps(body)}