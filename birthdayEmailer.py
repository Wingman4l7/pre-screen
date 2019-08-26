import redis
import asyncio
import datetime
import unittest


class TestBirthdayEmailer(unittest.TestCase):
  
  # def __init__(self, methodName='runTest'):
  #   today = datetime.date.today()

  # need to run a client to do tests...

  def test_isBirthday(self):
    testUser = User(1, datetime.date.today())
    self.assertTrue(testUser.isBirthday())
    testUser.birthday = today - datetime.timedelta(1)  # yesterday's date
    self.assertFalse(testUser.isBirthday())

  def test_hasSentThisYear(self):
    testUser = User(2, datetime.date.today()) 
    key = "sent-" + str(2)
    testUser.redis.set(key, today.year) 
    self.assertTrue(testUser.hasSentThisYear(key))
    testUser.redis.set(key, (today.year - 1)) 
    self.assertFalse()    

  def test_setSentStatus(self):  
    testUser = User(3, datetime.date.today())
    key = "sent-" + str(3)
    testUser.setSentStatus(key)
    self.assertEquals(testUser.redis.get(key), today.year)


class User:

  def __init__(self, id, birthday, client):
    self.id = id
    self.birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
    self.redis = client
  
  # made return function more explicit, so it is more easily readable
  # using the full year as part of the conditional will result in false negatives!  Removed.
  def isBirthday(self): 
    today = datetime.date.today()
    return self.birthday.month == today.month and self.birthday.day == today.day

  async def celebrateBirthday(self, key):
    hasSent = self.hasSentThisYear(key)
    if not hasSent:
      sendBirthdayEmail(key)
    self.setSentStatus(key)
  
  def hasSentThisYear(self, key):
    sentYear = self.redis.hget(key, 'sentYear')
    return sentYear == str(datetime.date.today().year)

  def setSentStatus(self, key):
    currentYear = datetime.date.today().year
    self.redis.hset(key, 'sentYear', currentYear)

  async def findUser(client, key):
    user = client.hgetall(key)
    return User(user["id"], user["birthday"], client)    


async def iterateOverUsers(client):
  # BEST PRACTICE: ( installed version of redis doesn't support scan_iter() )
  # for key in client.scan_iter("user-*"): # use built-in iterating function
  keys = client.keys('user-*')
  for key in keys:
    user = await User.findUser(client, key)
    if user.isBirthday():
      await user.celebrateBirthday(key)

# FOR TESTING
def addTestEntries(client):
  client.hmset('user-1', {'id' : '1', 'birthday' : '2000-12-30'})
  client.hmset('user-2', {'id' : '2', 'birthday' : '2000-08-25'})
  client.hmset('user-3', {'id' : '3', 'birthday' : '2000-08-25', 'sentYear' : '2019'})

# STUB function to get code to run completely:
def sendBirthdayEmail(key):
  print("It's " + key + " 's birthday!")

def main():

  # arguments should be set / accessed via config file:
  client = redis.StrictRedis(
  host="localhost",
  port=6379, 
  charset ="utf-8",
  decode_responses=True)

  addTestEntries(client)
  asyncio.run(iterateOverUsers(client))

# process main method call
if __name__ == '__main__':
  # unittest.main()
  main()