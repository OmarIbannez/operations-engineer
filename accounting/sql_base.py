from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from accounting.config import SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
DBSession = Session()
