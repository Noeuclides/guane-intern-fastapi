
import os
import urllib
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
print("*"*50)
print("<<<>>>>>>", BASE_DIR)

print(os.environ["DATABASE_URL"])
#app = FastAPI()
#app.add_middleware(DBSessionMiddleware,db_url=os.environ["DATABASE_URL"])

# configure database
host_server = os.environ.get('host_server', 'localhost')
db_server_port = urllib.parse.quote_plus(
    str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'guanedb1')
db_username = urllib.parse.quote_plus(
    str(os.environ.get('db_username', 'postgres')))
print(db_username)
db_password = urllib.parse.quote_plus(
    str(os.environ.get('db_password', 'secret')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode', 'prefer')))
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(
    db_username,
    db_password,
    host_server,
    db_server_port,
    database_name,
    ssl_mode
)
print(DATABASE_URL)
#print(os.environ["DATABASE_URL"])
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

