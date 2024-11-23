from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os
import jwt
import time

load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
JWT_SECRET = os.getenv("JWT_SECRET")

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
  return jwt.encode({"userId": userId, "createdAt": time.time}, JWT_SECRET, algorithm="HS256")

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
    return None
  userId = str(user["_id"])
  return createAuthorization(userId)

def getRoutineList(authorization: str) -> list:
  # Function to get a list of routines for a user
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  routines = routineCollection.find({
    "userId": userId,
  })
  for routine in routines:
    routine["_id"] = str(routine["_id"])  # Convert ObjectId to string
  return list(routines)

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
  return routine

def getSegmentsAvailable() -> list:
  # Function to get available segments
  return [] # hard coded for now

def createRoutine(authorization: str, name: str, description: str, segments: list) -> str:
  # Function to create a new routine and return its ID
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
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
  routineCollection.update_one({
    "_id": ObjectId(routineId),
    "userId": userId,
  }, {
    "$set": {
      "name": name,
      "description": description,
      "segments": segments,
    }
  })

def deleteRoutine(authorization: str, routineId: str) -> None:
  # Function to delete a routine by ID
  userId = validateAuthorization(authorization)
  routineCollection = get_routine_collection()
  routineCollection.delete_one({
    "_id": ObjectId(routineId),
    "userId": userId,
  })

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