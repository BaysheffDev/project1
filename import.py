import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,  sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))

def main() :
    # Create Table
    try:
        db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INT NOT NULL)")
        db.commit()
        print("BOOKS creation SUCCESSFUL.")
    except:
        print("BOOKS was NOT created.")

    try:
        db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")
        db.commit()
        print("USERS creation SUCCESSFUL.")
    except:
        print("USERS was NOT created.")

    try:
        db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, user_id INT NOT NULL, rating FLOAT(8), rating_text INT)")
        db.commit()
        print("REVIEWS creation SUCCESSFUL.")
    except:
        print("REVIEWS was NOT created.")

    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)

    #Insert each row of cvs file into database
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

    # Print a record after data has been inserted
    entries = db.execute("SELECT * FROM books")
    for row in entries:
        print(row)

if __name__ == "__main__":
    main()
