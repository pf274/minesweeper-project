from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os
import jwt
import time
from groq import Groq

from routineSegments import allAvailableSegments

load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ONE_HOUR = 3600

def validateAuthorization(authorization: str) -> str:
  # Function to validate an authorization token
  try:
    decodedJWT = jwt.decode(authorization, JWT_SECRET, algorithms=["HS256"])
    if "userId" not in decodedJWT:
      raise PermissionError("Invalid authorization token")
    if 'createdAt' not in decodedJWT:
      raise PermissionError("Invalid authorization token")
    createdAt = decodedJWT['createdAt']
    timeElapsed = time.time() - createdAt
    if timeElapsed > ONE_HOUR:
      raise PermissionError("Authorization token expired")
    return decodedJWT["userId"]
  except:
    raise PermissionError("Invalid authorization token")
  
def createAuthorization(userId: str) -> str:
  # Function to create an authorization token
  return jwt.encode({"userId": userId, "createdAt": time.time()}, JWT_SECRET, algorithm="HS256")

def get_db_connection():
  if DB_USERNAME is None or DB_PASSWORD is None:
    raise ValueError("Missing DB_USERNAME or DB_PASSWORD in environment variables")
  client = MongoClient(f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@morning.ed8fm.mongodb.net/?retryWrites=true&w=majority&appName=morning")
  db = client["morning"]
  return db

def get_user_collection():
  db = get_db_connection()
  return db["users"]

def get_routine_collection():
  db = get_db_connection()
  return db["routines"]

def test_connection():
  db = get_db_connection()
  return db.command("serverStatus")

def createUser(username: str, password: str, name: str) -> None:
  usersCollection = get_user_collection()
  usersCollection.insert_one({
    "name": name,
    "username": username,
    "password": password,
  })

def login(username: str, password: str) -> str:
  # Function to log in a user and return an auth token
  usersCollection = get_user_collection()
  user = usersCollection.find_one({
    "username": username,
    "password": password,
  })
  if user is None:
    raise PermissionError("Invalid username or password")
  userId = str(user["_id"])
  newAuthToken = createAuthorization(userId)
  print(f"New auth token: {newAuthToken}")
  return newAuthToken

def getRoutineList(authorization: str) -> list:
  # Function to get a list of routines for a user
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  routines = list(routineCollection.find({
    "userId": userId,
  }))
  for routine in routines:
    routine["_id"] = str(routine["_id"])  # Convert ObjectId to string
    routine.pop('userId', None)  # Remove userId from response
  return routines

def getRoutine(authorization: str, routineId: str) -> dict:
  # Function to get a routine by ID
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  routine = routineCollection.find_one({
    "_id": ObjectId(routineId),
    "userId": userId,
  })
  if routine is None:
    return None
  routine["_id"] = str(routine["_id"])  # Convert ObjectId to string
  routine.pop('userId', None)  # Remove userId from response
  availableSegmentNames = list(allAvailableSegments().keys())
  validSegments = []
  for segmentName in routine['segments']:
    if segmentName in availableSegmentNames:
      validSegments.append(segmentName)
  if len(validSegments) < len(routine['segments']):
    updateRoutine(authorization, routineId, routine['name'], routine['description'], validSegments)
  return routine

def performRoutine(authorization: str, routineId: str) -> str:
  print("Performing routine...")
  routine = getRoutine(authorization, routineId)
  if routine is None:
    return "So sorry, but I couldn't find that routine."
  availableSegmentNames = list(allAvailableSegments().keys())
  segmentText = [f"Today's Date: {time.strftime('%A, %B %d, %Y')}"]
  for segmentName in routine['segments']:
    print(f"Getting data for segment {segmentName}...")
    if segmentName in availableSegmentNames:
      segmentText.append(allAvailableSegments()[segmentName]())
  routineRawText = "\n".join(segmentText)
  client = Groq(api_key=GROQ_API_KEY)
  print("Getting chat completion...")
  chat_completion = client.chat.completions.create(
    messages=[
      {
        "role": "system",
        "content": f"Turn this JSON output into an entertaining morning show. Don't include any breaks or <insert content here> sections or non-verbal descriptions, and indicate speakers using \"Gerald: \" and \"Janice: \" at the beginning of each line. Besides speaker tags, ensure all other content is legible and proper english.\n{routineRawText}"
      }
    ],
    model="llama3-8b-8192"
  )
  print("Chat completion received.")
  if 'choices' not in chat_completion.__dict__ or len(chat_completion.choices) == 0 or 'message' not in chat_completion.choices[0].__dict__ or 'content' not in chat_completion.choices[0].message.__dict__:
    return "I'm sorry, I couldn't generate a morning show for you. Please try again later."
  return chat_completion.choices[0].message.content

def getSegmentsAvailable() -> list:
  # Function to get available segments
  return list(allAvailableSegments().keys())

def createRoutine(authorization: str, name: str, description: str, segments: list) -> str:
  # Function to create a new routine and return its ID
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  availableSegments = getSegmentsAvailable()
  if len(segments) > 0:
    for segment in segments:
      if segment not in availableSegments:
        raise ValueError(f"Invalid segment: {segment}")
  response = routineCollection.insert_one({
    "name": name,
    "description": description,
    "segments": segments,
    "userId": userId,
  })
  return str(response.inserted_id)

def updateRoutine(authorization: str, routineId: str, name: str, description: str, segments: list) -> None:
  # Function to update an existing routine
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  availableSegments = getSegmentsAvailable()
  if len(segments) > 0:
    for segment in segments:
      if segment not in availableSegments:
        raise ValueError(f"Invalid segment: {segment}")
  result = routineCollection.update_one({
    "_id": ObjectId(routineId),
    "userId": userId,
  }, {
    "$set": {
      "name": name,
      "description": description,
      "segments": segments,
    }
  })
  if result.matched_count == 0:
    raise PermissionError("Routine not found")

def deleteRoutine(authorization: str, routineId: str) -> None:
  # Function to delete a routine by ID
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  result = routineCollection.delete_one({
    "_id": ObjectId(routineId),
    "userId": userId,
  })
  if result.deleted_count == 0:
    raise PermissionError("Routine not found")

def getUser(authorization: str) -> dict:
  # Function to get user information based on authorization token
  userId = validateAuthorization(authorization)
  usersCollection = get_user_collection()
  user = usersCollection.find_one({
    "_id": ObjectId(userId),
  })
  if user is None:
    return None
  user["_id"] = str(user["_id"])  # Convert ObjectId to string
  return user

def updateUser(authorization: str, name: str) -> None:
  # Function to update user information
  userId = validateAuthorization(authorization)
  usersCollection = get_user_collection()
  usersCollection.update_one({
    "_id": ObjectId(userId),
  }, {
    "$set": {
      "name": name,
    }
  })