import json
from morningbusiness import createUser, login, getRoutine, getSegmentsAvailable, createRoutine, updateRoutine, deleteRoutine, getUser, updateUser, getRoutineList

def handler(event: dict, context: dict) -> dict:
  print(event)
  # get input data
  path = event['path']
  method = event['httpMethod']
  authorization = None
  if 'headers' in event and 'Authorization' in event['headers']:
    authorization = event['headers']['Authorization']
  elif 'requestContext' in event and 'authorizer' in event['requestContext'] and 'jwt' in event['requestContext']['authorizer']:
    authorization = event['requestContext']['authorizer']
  if type(authorization) is str and 'Bearer ' in authorization:
    authorization = authorization.replace('Bearer ', '')
  print(f"Authorization: {authorization}")
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
    if 'signup' in path and method == "POST":
      return handle_signup(inBody)
    elif 'login' in path and method == "POST":
      return handle_login(inBody)
    elif 'routine/list' in path and method == "GET":
      return handle_get_routine_list(authorization)
    elif 'routine/get' in path and method == "GET":
      return handle_get_routine(queryStringParameters, authorization)
    elif 'routine/segments_available' in path and method == "GET":
      return handle_get_segments_available(authorization)
    elif 'routine/create' in path and method == "POST":
      return handle_create_routine(inBody or {}, authorization)
    elif 'routine/update' in path and method == "POST":
      return handle_update_routine(inBody or {}, authorization)
    elif 'routine/delete' in path and method == "DELETE":
      return handle_delete_routine(queryStringParameters, authorization)
    elif 'user/get' in path and method == "GET":
      return handle_get_user(authorization)
    elif 'user/update' in path and method == "POST":
      return handle_update_user(inBody or {}, authorization)
    else:
      return generate_response(400, {"message": "Invalid path or method"})
  except Exception as e:
    return generate_response(500, {"message": str(e)})

def generate_response(statusCode: int, body: dict) -> dict:
  """
  Generates an HTTP response dictionary.
  Args:
    statusCode (int): The HTTP status code for the response.
    body (dict): The body of the response, which will be JSON-encoded.
  Returns:
    dict: A dictionary representing the HTTP response with keys 'statusCode', 'body', and 'headers'.
  """
  return {
    "statusCode": statusCode,
    "body": json.dumps(body),
    "headers": {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token, X-Amz-User-Agent"
    }
  }

def handle_signup(body: dict) -> dict:
  """
  Handles the request to sign up a new user.
  Args:
    body (dict): A dictionary containing the user's signup information. (username, encoded password, and name)
  Returns:
    dict: A response dictionary containing the status code and either a success message or an error message.
  The function performs the following steps:
  1. Parses the user's signup information from the provided body.
  2. If the signup information is invalid, returns a 400 response with an error message.
  3. If the signup information is valid, creates a new user account.
  4. Returns a 200 response with a success message.
  """
  # parse signup information
  requiredBodyParams = ['username', 'password', 'name']
  missingBodyParams = []
  for param in requiredBodyParams:
    if param not in body:
      missingBodyParams.append(param)
  if len(missingBodyParams) > 0:
    return generate_response(400, {"message": f"Missing body parameters: {', '.join(missingBodyParams)}"})
  username = body['username']
  password = body['password']
  name = body['name']
  createUser(username, password, name)
  return generate_response(200, {"message": "User signed up successfully! Please log in."})

def handle_login(body: dict) -> dict:
  """
  Handles the request to log in a user.
  Args:
    body (dict): A dictionary containing the user's login information. (username and encoded password)
  Returns:
    dict: A response dictionary containing the status code and either a success message or an error message.
  The function performs the following steps:
  1. Parses the user's login information from the provided body.
  2. If the login information is invalid, returns a 400 response with an error message.
  3. If the login information is valid, logs in the user.
  4. Returns a 200 response with a success message.
  """
  # parse login information
  requiredBodyParams = ['username', 'password']
  missingBodyParams = []
  for param in requiredBodyParams:
    if param not in body:
      missingBodyParams.append(param)
  if len(missingBodyParams) > 0:
    return generate_response(400, {"message": f"Missing body parameters: {', '.join(missingBodyParams)}"})
  username = body['username']
  password = body['password']
  authToken = login(username, password)
  return generate_response(200, {"message": "User logged in successfully!", "authToken": authToken})

def handle_get_routine_list(authorization: str) -> dict:
  """
  Handles the request to get a list of routines for a user.
  Args:
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either the user's routines or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. Retrieves the user's routines.
  4. Returns a 200 response with the user's routines.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  routines = getRoutineList(authorization)
  return generate_response(200, {"routines": routines})

def handle_get_routine(query: dict, authorization: str) -> dict:
  """
  Handles the request to get a user's routine.
  Args:
    query (dict): A dictionary containing the query parameters.
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either the user's routine or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. Retrieves the user's routine.
  4. Returns a 200 response with the user's routine.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  if 'id' not in query:
    return generate_response(400, {"message": "Missing query parameter: id"})
  routineId = query['id']
  routine = getRoutine(authorization, routineId)
  return generate_response(200, {"routine": routine})

def handle_get_segments_available(authorization: str) -> dict:
  """
  Handles the request to get available segments for a user's routine.
  Args:
    query (dict): A dictionary containing the query parameters.
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either the available segments or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. Retrieves the available segments for the user's routine.
  4. Returns a 200 response with the available segments.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  segments = getSegmentsAvailable()
  return generate_response(200, {"availableSegments": segments})

def handle_create_routine(body: dict, authorization: str) -> dict:
  """
  Handles the request to create a new routine for a user.
  Args:
    body (dict): A dictionary containing the routine information.
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either a success message or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. Parses the routine information from the provided body.
  4. If the routine information is invalid, returns a 400 response with an error message.
  5. If the routine information is valid, creates a new routine for the user.
  6. Returns a 200 response with a success message.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  requiredBodyParams = ['name', 'description', 'segments']
  missingBodyParams = []
  for param in requiredBodyParams:
    if param not in body:
      missingBodyParams.append(param)
  if len(missingBodyParams) > 0:
    return generate_response(400, {"message": f"Missing body parameters: {', '.join(missingBodyParams)}"})
  name = body['name']
  description = body['description']
  segments = body['segments']
  id = createRoutine(authorization, name, description, segments)
  return generate_response(200, {"message": "Routine created successfully!", "id": id})

def handle_update_routine(body: dict, authorization: str) -> dict:
  """
  Handles the request to update a user's routine.
  Args:
    body (dict): A dictionary containing the routine information.
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either a success message or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. Parses the routine information from the provided body.
  4. If the routine information is invalid, returns a 400 response with an error message.
  5. If the routine information is valid, updates the user's routine.
  6. Returns a 200 response with a success message.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  requiredBodyParams = ['id', 'name', 'description', 'segments']
  missingBodyParams = []
  for param in requiredBodyParams:
    if param not in body:
      missingBodyParams.append(param)
  if len(missingBodyParams) > 0:
    return generate_response(400, {"message": f"Missing body parameters: {', '.join(missingBodyParams)}"})
  routineId = body['id']
  name = body['name']
  description = body['description']
  segments = body['segments']
  updateRoutine(authorization, routineId, name, description, segments)
  return generate_response(200, {"message": "Routine updated successfully!"})

def handle_delete_routine(query: dict, authorization: str) -> dict:
  """
  Handles the request to delete a user's routine.
  Args:
    query (dict): A dictionary containing the query parameters.
    authorization (str): The user's authorization token.
  Returns:
    dict: A response dictionary containing the status code and either a success message or an error message.
  The function performs the following steps:
  1. Validates the user's authorization token.
  2. If the authorization token is invalid, returns a 401 response with an error message.
  3. If the routine ID is missing, returns a 400 response with an error message.
  4. Deletes the user's routine.
  5. Returns a 200 response with a success message.
  """
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  if 'id' not in query:
    return generate_response(400, {"message": "Missing query parameter: id"})
  routineId = query['id']
  deleteRoutine(authorization, routineId)
  return generate_response(200, {"message": "Routine deleted successfully!"})

def handle_get_user(authorization: str) -> dict:
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  user = getUser(authorization)
  return generate_response(200, {"user": user})

def handle_update_user(body: dict, authorization: str) -> dict:
  if authorization is None:
    return generate_response(401, {"message": "There be no auth token, matey!"})
  requiredBodyParams = ['name']
  missingBodyParams = []
  for param in requiredBodyParams:
    if param not in body:
      missingBodyParams.append(param)
  if len(missingBodyParams) > 0:
    return generate_response(400, {"message": f"Missing body parameters: {', '.join(missingBodyParams)}"})
  name = body['name']
  updateUser(authorization, name)
  return generate_response(200, {"message": "User updated successfully!"})