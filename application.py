import os
import requests

from flask import Flask, session, jsonify, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Goodreads KEY
key = "mLyb4WtEDK4Tcp76Bm2uyw"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

####################################
####  Routes  ######################

# home / search page
@app.route("/", methods=["POST", "GET"])
@login_required
def index():

    if request.method == "POST":

        return render_template("index.html")
    else:
        return render_template("index.html")

# Books page
@app.route("/books", methods=["POST"])
@login_required
def books():

    if request.method == "POST":
        search = request.form.get("book_search")

        isbn_rating = request.form.get("book_id_rating")
        isbn_review = request.form.get("book_id_review")

        rating = request.form.get("rating")
        review = request.form.get("review")

        # Update database with new rating
        if isbn_rating:
            # Check if entry exists
            result = db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND user_id=:user_id",
                                {"isbn": isbn_rating, "user_id": session["user_id"]}).fetchone()
            # If entry doesn't exists insert
            if not result:
                db.execute("INSERT INTO reviews (isbn, user_id, rating) VALUES (:isbn, :user_id, :rating)",
                           {"isbn": isbn_rating, "user_id": session["user_id"], "rating": rating})
                db.commit()
            # Else update
            else:
                db.execute("UPDATE reviews SET rating=:rating WHERE id=:id",
                           {"rating": rating, "id": result[0]})
                db.commit()

        # Update database with new review
        if isbn_review:
            # Check if entry exists
            result = db.execute("SELECT * FROM reviews WHERE isbn=:isbn AND user_id=:user_id",
                                {"isbn": isbn_review, "user_id": session["user_id"]}).fetchone()
            # If entry doesn't exists insert
            if not result:
                db.execute("INSERT INTO reviews (isbn, user_id, rating_text) VALUES (:isbn, :user_id, :rating_text)",
                           {"isbn": isbn_review, "user_id": session["user_id"], "rating_text": review})
                db.commit()
            # Else update
            else:
                db.execute("UPDATE reviews SET rating_text=:rating_text WHERE id=:id",
                           {"rating_text": review, "id": result[0]})
                db.commit()

        # Refresh page with same search results if user just updated a rating or review
        if search == None :
            search = request.form.get("stored_search")
        else:
            search = search.lower()

        # get books from database matching search text
        result = db.execute("SELECT id, isbn, title, author, year FROM books WHERE LOWER(isbn) LIKE :book OR LOWER(title) LIKE :book OR LOWER(author) LIKE :book",
                            {"book": "%" + search + "%"}).fetchall()
        # Check if books are found
        if not result:
            message = "No books were found. Please search again."
            return render_template("books.html", message=message)

        # Store Goodreads review data
        review_data = []
        # retrieve and store review data for matching books
        for book in result:
            isbn = book[1]
            data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
            data = data.json()
            data = data["books"][0]
            number_of_ratings = data["work_ratings_count"]
            average_rating = data["average_rating"]
            review_data.append((number_of_ratings, average_rating))

        book_data = result

        user_reviews = []
        # Get user ratings
        for book in result:
            data = db.execute("SELECT rating, rating_text FROM reviews WHERE isbn=:isbn AND user_id=:user_id",
                                {"isbn": book[1], "user_id": session["user_id"]}).fetchone()
            if not data:
                user_reviews.append((0, ""))
            elif not data[0]:
                user_reviews.append((0, data[1]))
            elif not data[1]:
                user_reviews.append((data[0], ""))
            else:
                user_reviews.append((data[0], data[1]))

        # return str(user_reviews)

        return render_template("books.html", search=search, books=book_data, reviews=review_data, user_reviews=user_reviews)

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):

    if request.method == "GET":
        data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
        data = data.json()
        data = data["books"][0]
        number_of_ratings = data["work_ratings_count"]
        average_rating = data["average_rating"]

        result = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()

        obj = {
            "title": result[2],
            "author": result[3],
            "year": result[4],
            "isbn": result[1],
            "review_count": number_of_ratings,
            "average_score": average_rating,
        }

        return jsonify(obj)

#Register
@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"),
                                method='pbkdf2:sha256', salt_length=8)

        result = db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).fetchone()
        # If user doesn't exist, create user
        if not result:
            db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
                        {"username": username, "password": password})
            db.commit()

            # Get new user to store session id
            user =  db.execute("SELECT id FROM users WHERE username=:username", {"username": username}).fetchone()
            session["user_id"] = user[0]
            return redirect("/")
        # If user exists, return error message
        else:
            message = "Username already exists"
            return render_template("register.html", message=message)
    else:
        return render_template("register.html", message=message)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        result = db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).fetchone()
        # Check username and password exist
        if not result or not check_password_hash(result[2], password):
            message = "Login details incorrect"
            return render_template("login.html", message=message)
        else:
            session["user_id"] = result[0]
            return redirect("/")
    else:
        return render_template("login.html", message=message)

#Logout
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()
    return redirect("/")
