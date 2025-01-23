from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE = 'postgresql://postgres:@localhost:5432/misa_db'

engine = create_engine(URL_DATABASE)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()