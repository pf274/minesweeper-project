import requests
import time
import random


def spaceNews():
  def fromToday(ISODateString: str):
    timeNow = time.time()
    date = time.strptime(ISODateString, "%Y-%m-%dT%H:%M:%S%z")
    publishedDate = time.mktime(date)
    timeElapsed = timeNow - publishedDate
    hoursElapsed = timeElapsed / 3600
    if hoursElapsed <= 24:
      return True
    return False
  url = "https://api.spaceflightnewsapi.net/v4/articles/"
  response = requests.get(url, timeout=10)
  if not response.ok:
    return ""
  data = response.json()
  articles = [article for article in data['results'] if fromToday(article['published_at'])]
  if len(articles) == 0:
    return "There are no space news articles for today"
  randomArticle = random.choice(articles)
  return f"Here's a space news article for today: {randomArticle['title']} - {randomArticle['summary']}"

def chuckNorrisJoke():
  url = "https://api.chucknorris.io/jokes/random"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  joke: str = data['value']
  return f"Here's a Chuck Norris joke: {joke}"

def geekJoke():
  url = "https://geek-jokes.sameerkumar.website/api?format=json"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  joke = data['joke']
  return f"Here is a geek joke: {joke}"

def dadJoke():
  url = "https://icanhazdadjoke.com/"
  response = requests.get(url, headers={"Accept": "application/json"})
  if not response.ok:
    return ""
  data = response.json()
  joke = data['joke']
  return f"Here's a dad joke: {joke}"

def punchlineJoke():
  url = "https://official-joke-api.appspot.com/random_joke"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  joke = f"{data['setup']} {data['punchline']}"
  return f"Here's a joke: {joke}"

def dogFact():
  url = "https://dogapi.dog/api/v2/facts"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  fact = data['data'][0]['attributes']['body']
  return f"Here's a fact about dogs: {fact}"

def catFact():
  url = "https://meowfacts.herokuapp.com/"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  fact = data['data'][0]
  return f"Here's a fact about cats: {fact}"

def unsolicitedAdvice():
  url = "https://api.adviceslip.com/advice"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  advice = data['slip']['advice']
  return f"Here's some unsolicited advice: {advice}"

def todaysRandomFact():
  url = "https://uselessfacts.jsph.pl/api/v2/facts/today"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  fact = data['text']
  return f"Here's the daily random fact: {fact}"

def randomFact():
  url = "https://uselessfacts.jsph.pl/api/v2/facts/random"
  response = requests.get(url)
  if not response.ok:
    return ""
  data = response.json()
  fact = data['text']
  return f"Here's a random fact: {fact}"

def numberFact():
  dayOfMonth = time.localtime().tm_mday
  month = time.strftime("%B")
  url = f"http://numbersapi.com/{dayOfMonth}/trivia"
  response = requests.get(url)
  if not response.ok:
    return ""
  fact = response.text
  return f"Today is day {dayOfMonth} of {month}. Here's a fact about the number {dayOfMonth}: {fact}"

def allAvailableSegments():
  return {
    "spaceNews": spaceNews,
    "chuckNorrisJoke": chuckNorrisJoke,
    "geekJoke": geekJoke,
    "dadJoke": dadJoke,
    "punchlineJoke": punchlineJoke,
    "dogFact": dogFact,
    "catFact": catFact,
    "unsolicitedAdvice": unsolicitedAdvice,
    "todaysRandomFact": todaysRandomFact,
    "randomFact": randomFact,
    "numberFact": numberFact,
  }

catFact()