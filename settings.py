from worker import MessageWorker
from database import DataBase
from configparser import ConfigParser

global parser
parser = ConfigParser()
parser.read('assets/settings.ini')

global db
db = DataBase(
    basefile='main.db',
    scheme='assets/main.db.sql')

global worker
worker = MessageWorker(db=db)
