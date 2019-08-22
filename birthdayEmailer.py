from redis import createClient
from localLibs import sendBirthdayEmail
import asyncio
import datetime
import unittest


class TestBirthdayEmailer(unittest.TestCase):
  
  today = datetime.date.today()

  def test_isBirthday(self):
    testUser = User(1, today)
    self.assertTrue(testUser.isBirthday())
    testUser.birthday = today - datetime.timedelta(1)  # yesterday's date
    self.assertFalse(testUser.isBirthday())

  def test_hasSentThisYear(self):
    testUser = User(2, today) 
    key = "sent-" + str(2)
    testUser.redis.set(key, today.year) 
    self.assertTrue(testUser.hasSentThisYear(key))
    testUser.redis.set(key, (today.year - 1)) 
    self.assertFalse()    

  def test_setSentStatus(self):  
    testUser = User(3, today)
    key = "sent-" + str(3)
    testUser.setSentStatus(key)
    self.assertEquals(testUser.redis.get(key), today.year)


class User:

  def __init__(self, id, birthday):
    self.id = id  # cleaner constructor
    self.birthday = birthday
    self.redis = redis.createClient()

  
  # made return function more explicit, so it is more easily readable
  # using the full year as part of the conditional will result in false negatives!  Removed.
  def isBirthday(): 
    today = datetime.date.today()
    if self.birthday.month == today.month and 
       self.birthday.day == today.day:
      return True
    else:
      return False

  async def celebrateBirthday():
    key = "sent-" + str(self.id)  
    hasSent = await self.hasSentThisYear(key)
    if not hasSent:
      await sendBirthdayEmail()
    await self.setSentStatus(key)
    # self.saveBirthday()  # not used

  # DEPRECATED -- not used!
  # def saveBirthday():  # more descriptive function name was needed
  #   self.redis.hset('users', self.id, 'birthday', self.birthday.toISOString())
  #   # would be better to have 'birthday' value be Date object, if supported by redis.
  
  def hasSentThisYear(key):
    sentYear = self.redis.get(key)
    if sentYear == datetime.date.today().year:
      return True
    else:
      return False

  def setSentStatus(key):
    currentYear = datetime.date.today().year
    self.redis.set(key, currentYear); 

  @staticmethod
  async def findUser(id):  # needed a more consistent/explanatory function name
    user = await new User().redis.hget('users', id)
    return new User(user.id, new Date(user.birthday))

  def iterateOverUsers():
    client = createClient()
    IdSet = await client.get('age-app:user-ids')
    for i in range(IdSet):
      user = await User.findUser(i)
      if user.isBirthday():
        await user.celebrateBirthday()


  async def main():
    iterateOverUsers()

# process main method call
if __name__ == '__main__':
    main()