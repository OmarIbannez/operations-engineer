import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.abspath("accounting.sqlite")
