import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,  sessionmaker

engine = create_engine(os.getenv("postgres://htxfhecbrwhcmj:3e9fb0da941fa6fd74d20592cd05e70f688662b5ea38a0baffa09961438a02ec@ec2-54-83-50-174.compute-1.amazonaws.com:5432/dc9t1miprngjge
"))
db = scoped_session(sessionmaker(bind=engine))

def main() :
    f = open("books.csv")
    reader = csv.reader(f)
    for column1, column2, column3 in reader:
        db.execute("")

if __name__ == "__main__":
