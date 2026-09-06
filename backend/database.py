import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# reads .env so its values become available below
load_dotenv()

# reusable connection manager pointed at our Postgres database
engine = create_engine(os.environ["DATABASE_URL"])

# base class every table in tables.py inherits from
Base = declarative_base()
