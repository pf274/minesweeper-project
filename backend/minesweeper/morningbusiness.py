import os
import time
import hmac
import requests
import hashlib
import base64
import json
from redis import Redis as RedisSetup
from redis.client import Redis as RedisClient
from routineSegments import allAvailableSegments
import random
import struct
import rsa

def rsaStringToPrivateKey(keyString: str) -> rsa.PrivateKey:
  return rsa.PrivateKey.load_pkcs1(keyString.replace("\\n", "\n").encode('utf-8'))

def newObjectId() -> str:
  """
  An object id is a 12-byte unique identifier consisting of:
  - a 4-byte value representing the seconds since the Unix epoch,
  - a 5-byte random value,
  - a 3-byte counter, starting with a random value.
  """
  timestamp = int(time.time())
  random_value = random.getrandbits(40)
  counter = random.getrandbits(24)
  object_id = struct.pack(">I5s3s", timestamp, random_value.to_bytes(5, 'big'), counter.to_bytes(3, 'big'))
  return object_id.hex()

def load_env_file(filepath: str):
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

load_env_file('./.env')

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
JWT_SECRET = os.environ.get("JWT_SECRET")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_DB = os.environ.get("REDIS_DB")
RSA_PRIVATE_KEY = os.environ.get("RSA_PRIVATE_KEY")

print("SUCCESS: Secrets loaded" if JWT_SECRET is not None and GROQ_API_KEY is not None and RSA_PRIVATE_KEY is not None else "ERROR: Secrets not loaded")

RSA_PRIVATE_KEY = rsaStringToPrivateKey(RSA_PRIVATE_KEY)
  
def decrypt(encryptedString: str) -> str:
  try:
    encryptedBytes = base64.b64decode(encryptedString.encode('utf-8'))
    decryptedBytes = rsa.decrypt(encryptedBytes, RSA_PRIVATE_KEY)
    return decryptedBytes.decode('utf-8')
  except Exception as e:
    raise ValueError("Error rsa decrypting string: " + str(e))

reusableRedisConnection = None

def get_redis_connection() -> RedisClient:
  global reusableRedisConnection
  if reusableRedisConnection is not None:
    return reusableRedisConnection
  r: RedisClient = RedisSetup(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    username="default",
    password=REDIS_PASSWORD,
    db=REDIS_DB
  )
  reusableRedisConnection = r
  return reusableRedisConnection

ONE_HOUR = 3600

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def encode_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload).encode('utf-8'))
    signature = hmac.new(secret.encode('utf-8'), f"{header_b64}.{payload_b64}".encode('utf-8'), hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_jwt(token: str, secret: str) -> dict:
    header_b64, payload_b64, signature_b64 = token.split('.')
    signature_check = hmac.new(secret.encode('utf-8'), f"{header_b64}.{payload_b64}".encode('utf-8'), hashlib.sha256).digest()
    if not hmac.compare_digest(base64url_decode(signature_b64), signature_check):
        raise PermissionError("Invalid authorization token")
    return json.loads(base64url_decode(payload_b64))

def validateAuthorization(authorization: str) -> tuple[str, str]:
  """
  Returns:
    tuple[str, str]: The user ID and username from the authorization token
  Raises:
    PermissionError: If the authorization token is invalid or expired
  """
  # Function to validate an authorization token
  try:
    decodedJWT = decode_jwt(authorization, JWT_SECRET)
    if "userId" not in decodedJWT:
      raise PermissionError("Invalid authorization token")
    if 'createdAt' not in decodedJWT:
      raise PermissionError("Invalid authorization token")
    createdAt = decodedJWT['createdAt']
    timeElapsed = time.time() - createdAt
    if timeElapsed > ONE_HOUR:
      raise PermissionError("Authorization token expired")
    return decodedJWT["userId"], decodedJWT["username"]
  except:
    raise PermissionError("Invalid authorization token")
  
def createAuthorization(userId: str, username: str) -> str:
  # Function to create an authorization token
  return encode_jwt({"userId": userId, "username": username, "createdAt": time.time()}, JWT_SECRET)

def createUser(username: str, encryptedPassword: str, name: str) -> None:
  redisClient: RedisClient = get_redis_connection()
  decrypt(encryptedPassword) # Test decryption
  redisClient.set(f"users-{username}", json.dumps({
    "_id": newObjectId(),
    "name": name,
    "username": username,
    "password": encryptedPassword,  # Store the encrypted password
  }))

def login(username: str, encryptedPassword: str) -> str:
  # Function to log in a user and return an auth token
  redisClient = get_redis_connection()
  redisUser = redisClient.get(f"users-{username}")
  if redisUser is not None:
    redisUser = json.loads(redisUser)
  if redisUser is None or decrypt(redisUser["password"]) != decrypt(encryptedPassword):  # Decrypt and compare the password
    raise PermissionError("Invalid username or password")
  userId = str(redisUser["_id"])
  newAuthToken = createAuthorization(userId, username)
  print(f"New auth token: {newAuthToken}")
  return newAuthToken

def checkUsernameAvailable(username: str) -> bool:
  # Function to check if a username is available
  redisClient = get_redis_connection()
  redisUser = redisClient.get(f"users-{username}")
  return redisUser is None

def getRoutineList(authorization: str) -> list:
  # Function to get a list of routines for a user
  userId, _ = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  routineKeys = redisClient.keys(f"routines-{userId}-*")
  if len(routineKeys) == 0:
    return []
  routines = redisClient.mget(routineKeys)
  if routines is None:
    return []
  else:
    routines = [json.loads(routine) for routine in routines]
  for routine in routines:
    routine.pop('userId', None)  # Remove userId from response
  return routines

def getRoutine(authorization: str, routineId: str) -> dict:
  # Function to get a routine by ID
  userId, _ = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  routine = redisClient.get(f"routines-{userId}-{routineId}")
  if routine is None:
    return None
  else:
    routine = json.loads(routine)
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
  groqURL = "https://api.groq.com/openai/v1/chat/completions"
  adjectives = [
    "enthusiastic",
    "bored",
    "sarcastic",
    # "angry",
    "sleepy",
    "excited",
    "happy",
    # "sad",
    "clueless",
    "drunk",
    "an intellectual",
    "a conspiracy theorist",
    "a communist"
  ]
  geraldAdjective = random.choice(adjectives)
  janiceAdjective = random.choice([adjective for adjective in adjectives if adjective != geraldAdjective])
  print(f"Gerald: {geraldAdjective}")
  print(f"Janice: {janiceAdjective}")
  groqResponse = requests.post(groqURL, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json={
    "messages": [
      {
        "role": "system",
        "content": f"Turn this JSON output into an entertaining morning show. Don't include any breaks or <insert content here> sections or non-verbal descriptions, and indicate speakers using \"Gerald: \" and \"Janice: \" at the beginning of each line. Gerald is {geraldAdjective} and Janice is {janiceAdjective}. Besides speaker tags, ensure all other content is legible and proper english.\n{routineRawText}"
      }
    ],
    "model": "llama3-8b-8192"
  })
  chat_completion = groqResponse.json()
  print("Chat completion received.")
  if 'choices' not in chat_completion or len(chat_completion['choices']) == 0 or 'message' not in chat_completion['choices'][0] or 'content' not in chat_completion['choices'][0]['message']:
    return "I'm sorry, I couldn't generate a morning show for you. Please try again later."
  morningShow = chat_completion['choices'][0]['message']['content']
  morningShow = [line for line in morningShow.replace("Gerald: ", "\nGerald: ").replace("Janice: ", "\nJanice: ").split("\n") if line.strip() != ""]
  morningShow = "\n\n".join(morningShow)
  return morningShow

def getSegmentsAvailable() -> list:
  # Function to get available segments
  return list(allAvailableSegments().keys())

def createRoutine(authorization: str, name: str, description: str, segments: list) -> str:
  # Function to create a new routine and return its ID
  userId, _ = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  availableSegments = getSegmentsAvailable()
  if len(segments) > 0:
    for segment in segments:
      if segment not in availableSegments:
        raise ValueError(f"Invalid segment: {segment}")
  if len(segments) > 5:
    raise ValueError("Too many segments. Maximum of 5 segments allowed.")
  newId = str(newObjectId())
  redisClient.set(f"routines-{userId}-{newId}", json.dumps({
    "name": name,
    "description": description,
    "segments": segments,
    "userId": userId,
    "_id": newId,
  }))
  return newId

def updateRoutine(authorization: str, routineId: str, name: str, description: str, segments: list) -> None:
  # Function to update an existing routine
  userId, _ = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  availableSegments = getSegmentsAvailable()
  if len(segments) > 0:
    for segment in segments:
      if segment not in availableSegments:
        raise ValueError(f"Invalid segment: {segment}")
  exists = redisClient.get(f"routines-{userId}-{routineId}") is not None
  if not exists:
    raise PermissionError("Routine not found")
  redisClient.set(f"routines-{userId}-{routineId}", json.dumps({
    "name": name,
    "description": description,
    "segments": segments,
    "userId": userId,
    "_id": routineId,
  }))

def deleteRoutine(authorization: str, routineId: str) -> None:
  # Function to delete a routine by ID
  userId, _ = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  deletedCount = redisClient.delete(f"routines-{userId}-{routineId}")
  if deletedCount == 0:
    raise PermissionError("Routine not found")

def getUser(authorization: str) -> dict:
  # Function to get user information based on authorization token
  _, username = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  user = redisClient.get(f"users-{username}")
  if user is None:
    return None
  user = json.loads(user)
  return user

def updateUser(authorization: str, name: str) -> None:
  # Function to update user information
  _, username = validateAuthorization(authorization)
  redisClient = get_redis_connection()
  user = redisClient.get(f"users-{username}")
  if user is None:
    raise PermissionError("User not found")
  user = json.loads(user)
  user["name"] = name
  redisClient.set(f"users-{username}", json.dumps(user))