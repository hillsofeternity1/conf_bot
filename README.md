# Full burst ultimate storm revolution Telegram Conference Bot

# Create your own spy bot in Telegram ¯\_(ツ)_/¯

This bot is able to get every message in your group, log it and send simple stat about top 10 used words. 


/code - highlight any code snippet following command. There is lexer guesser but you are able to specify language by adding last line comment like this:
```
/code
class Cat {
  constructor(name) {
    this.name = name;
  }
}
function get_name(any_object) {
  console.log(any_object.name);
}
var my_cat = new Cat('Cassandra');
get_name(my_cat)
#js
```
/sql - perform an SQL request to internal bot SQLite database. Any WRITE requests are prohibited.
/stat - your top 10 words in conf.

Also bot can summon every active member of group with @here command or just with mentioning bot username like @test_huy_bot .
**Copyright** 

*As probabilistic morphological analyzer (PMA) this bot uses mystem app, which developed by yandex and provided as binary package.*
*Also you can use free and open PMA tool like stemka and so on.*
