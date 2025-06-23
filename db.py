from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine('sqlite:///db.sqlite')
SessionLocal = sessionmaker(engine, autoflush=False, autocommit=False)
Base = declarative_base()
