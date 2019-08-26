
Updated Submission
================== 

Code is running now!  Test suite also works.

__Q:__ Your user class instantiates a redis client on every instance. This seems inefficient.

__A:__ It most certainly is!  This also might result in weird behavior at runtime.  It also masks other errors, such as the first line of `findUser()`.

__Q:__ Why the explicit returns for true false?  Could you not simply return the result of your comparison which is boolean?

__A:__  Absolutely!  Actually, when I intially refactored `hasSentThisYear()`, I replaced the unnecessary ternany operator expression `return this.redis.get(key) ? true : false;` with the simpler `return this.redis.get(key)`, before later changing entirely what the function returned.  Generally, I do not think that returning the result of a conditional, rather than an explicit boolean, is best practice in terms of readability, but I understand that it can make for tighter code.  As it doesn't affect functionality, this is something I'd usually catch / modify on a second or third pass, or adhere to whatever is the team's common practice.

__Q:__ The findUser function was a big prob of the jr dev's code. 

__A:__ Yes!  I looked closer at it when I was getting the code in working order.  It had a couple major issues.  The main one was the attempted creation of *two* `User` objects -- one created when fetching the user ID, and one created in the return statement -- when the intent is to only have one.  The first line would have failed anyway, as it is trying to create the `User` object without passing the required arguments.  


Initial Submission
==================

### Best Practices Being Violated: ###
* Moved the iteration of the userbase out of the `main()` method and into its own function.

### Problems At Scale: ###
* If you iterate through the entire user database to check birthdays against the current date, every time this runs, it will take longer and longer as your userbase grows.  It needs a smarter iterative approach that only touches the users whose birthday it is.
    * You could possibly use a command like `client.hgetall('birthday', today)`, if the redis was populated with a separate birthdate key whose values were day-month pairs __only__ *(omitting the year)*.

* Also, as this is a shared database, the a `get` of the entire userbase would become increasingly larger, and might have a performance impact that could affect other applications.

### Issues with Consistency, Naming Conventions: ###
* These were fixed where they were found, and noted in an accompanying comment.
    * One example was the generic static function `find()`, whose name did not specify what it was finding.  
    * Another was declaring the variable for the newly created redis client object with the nondescript letter `r`.

### What Do I Disagree With? ###
* There's not really a need for the `hasSentThisYear()` function or accompanying key.  Given the current structure, all users are iterated over.
* The `setSentStatus()` function does not need to create an expiring key -- instead, you can compare the current year to the last year that the message was sent.

### Edge Cases Not Thought Of? ###
* Using a `setSentStatus()` key expiration duration of seconds based on a 365 day year would mean eventual drift, once 366 day leap years began to pass.
* Another possible issue would be birthday emails arriving early or late from the perspective of the user, depending on their timezone relative to the timezone set on the system running the cron job.
* If a user changes their birthday details and these are updated in the database, you would potentially need to decrement the year value paired to the key represented the most recent year they received a birthday email.
