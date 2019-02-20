import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,  sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))

def main() :
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        #SQL query
        print(f"line 1: {isbn},  {title}, {author}, {year} ")
        # db.execute("")
        # print() - for clarity
    # db.commit()

if __name__ == "__main__":
    main()
