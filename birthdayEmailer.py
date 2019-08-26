import redis
import asyncio
import datetime
import unittest


class TestBirthdayEmailer(unittest.TestCase):
  
  def setUp(self):
    self.redis = redis.StrictRedis(
    host="localhost",
    port=6379, 
    encoding ="utf-8",
    decode_responses=True)

    self.today = datetime.date.today()
    self.testUser = User(2, str(self.today), self.redis)
    self.key = "user-2"
    self.redis.hmset('user-2', {'id' : '2', 'birthday' : '2000-08-25'})

  def tearDown(self):
    pass # no need to close connection, Redis handles automatically

  def test_isBirthday(self):
    self.assertTrue(self.testUser.isBirthday())
    self.testUser.birthday = datetime.date.today() - datetime.timedelta(1)  # yesterday's date
    self.assertFalse(self.testUser.isBirthday())

  def test_hasSentThisYear(self):
    self.redis.hset(self.key, 'sentYear', self.today.year)
    self.assertTrue(self.testUser.hasSentThisYear(self.key))
    self.redis.hset(self.key, 'sentYear', (self.today.year - 1))  # last yaer
    self.assertFalse(self.testUser.hasSentThisYear(self.key))    

  def test_setSentStatus(self):
    self.testUser.setSentStatus(self.key)
    self.assertEqual(self.testUser.redis.hget(self.key, 'sentYear'), str(self.today.year))
    self.assertNotEqual(self.testUser.redis.hget(self.key, 'sentYear'), str(self.today.year - 1))


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

# stub function to get code to run completely:
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