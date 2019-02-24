import os
import requests

from flask import Flask, session, jsonify, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

def index():

    if request.method == "POST":

        return render_template("index.html")
    else:
        return render_template("index.html")

# Books page
@app.route("/books", methods=["POST"])

def books():

    if request.method == "POST":
        search = request.form.get("book_search")
        isbn_rating = request.form.get("book_id_rating")
        isbn_review = request.form.get("book_id_rating")

        # Update database with new rating
        if isbn_rating:
            # Check if entry exists
            result = db.execute("SELECT * WHERE isbn=:isbn AND user_id=:user_id",
                                {"isbn": isbn_rating, "user_id": session["user_id"]}).fetchall()
            # If entry doesn't exists insert
            if not result:
                db.execute("INSERT INTO reviews (isbn, user_id, rating, rating_text) VALUES (:isbn, :user_id, :rating, :rating_text)",
                           {"isbn": isbn, "title": title, "author": author, "year": year})
            # Else update
            else:
                db.execute("UPDATE reviews SET rating=:rating WHERE id=:id",
                           {"rating": rating, "id": id})

        # Update database with new rating
        if isbn_review:
            # Check if entry exists
            result = db.execute("SELECT id, isbn, title, author, year FROM books WHERE LOWER(isbn) LIKE :book OR LOWER(title) LIKE :book OR LOWER(author) LIKE :book",
                                {"book": "%" + search + "%"}).fetchall()

            # If entry exists update

            # Else insert
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                       {"isbn": isbn, "title": title, "author": author, "year": year})

        # Refshesh page with same search results if user just updated a rating or review
        if search:
            search = search.lower()
        else:
            search = request.form.get("stored_search")

        # get books from database matching search text
        result = db.execute("SELECT id, isbn, title, author, year FROM books WHERE LOWER(isbn) LIKE :book OR LOWER(title) LIKE :book OR LOWER(author) LIKE :book",
                            {"book": "%" + search + "%"}).fetchall()
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
        test  = "testclass"

        return render_template("books.html", search=search, books=book_data, reviews=review_data, test=test)


@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):

    if request.method == "GET":
        data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
        data = data.json()

        return jsonify(data)


#Register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    message = ""

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
        db.execute("SELECT * FROM users WHERE username=?", {"username": username})
        result = db.fetchone()
        if not result or not check_password_hash(result[0][3], password):
            message = "Login details incorrect"
            return render_template("login.html", message=message)
        else:
            session["user_id"] = result[0][0]
            return redirect("/")
    else:
        return render_template("login.html", message=message)

#Logout
@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
