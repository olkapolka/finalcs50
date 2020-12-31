import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.route("/")
# @login_required
def index():
    """Show main page"""
    articles = db.execute("SELECT username, article_id, title, image, date, author_id FROM articles JOIN users ON users.id=articles.author_id ORDER BY date DESC")

    return render_template("index.html", articles=articles)

@app.route("/add-news", methods=["GET", "POST"])
@login_required
def addNews():
    """Create news"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            return apology("Please provide title")
        # Ensure text was submitted
        elif not request.form.get("text"):
            return apology("Please provide text")
        # Ensure category was submitted
        elif not request.form.get("category"):
            return apology("Please provide category")
        # Ensure user is authorized
        elif not session["user_id"]:
            return apology("Anonymous users are not allowed to add news")
        else:
            # add news to database
            db.execute("INSERT INTO articles (title, image, text, author_id, date, category_id_article) VALUES (:title, :image, :text, :author_id, :date, :category_id)",
                title=request.form.get("title"), image=request.form.get("image"), text=request.form.get("text"), author_id=session["user_id"], date=datetime.now(), category_id=request.form.get("category"))

            # Show message
            return render_template("add-news.html", showMessage=True)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        currentCategories = db.execute("SELECT * FROM categories")
        return render_template("add-news.html", currentCategories=currentCategories)

@app.route('/article', methods=["GET", "POST"])
def article_route():
    id = request.args.get('id', default = 1, type = int)
    article = db.execute("SELECT article_id, username, title, image, text, date, author_id, category_id_article, category_id, category_title FROM articles JOIN users ON users.id=articles.author_id JOIN categories ON categories.category_id=articles.category_id_article WHERE article_id=:id",
                            id=id)
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure name of comment's author was submitted
        if not request.form.get("name"):
            return apology("Please provide name")
        elif not request.form.get("text"):
            return apology("Please provide name")
        else:
            # add new comment to database
            db.execute("INSERT INTO comments (author_comment, text_comment, article_id_comment, date_comment) VALUES (:author, :text, :article_id, :date)",
                author=request.form.get("name"), text=request.form.get("text"), article_id=request.form.get("article_id"), date=datetime.now())

            # get comments for this article
            comments = db.execute("SELECT author_comment, text_comment, date_comment FROM comments WHERE article_id_comment=:id ORDER BY date_comment",
                            id=article[0]["article_id"])
            return render_template("article.html", article=article[0], comments=comments, showMessage=True)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # get comments for this article
        comments = db.execute("SELECT author_comment, text_comment, date_comment FROM comments WHERE article_id_comment=:id ORDER BY date_comment",
                            id=article[0]["article_id"])
        return render_template("article.html", article=article[0], comments=comments)

@app.route("/categories", methods=["GET", "POST"])
def categories():
    """Create new category"""
    if (session and session['user_id']):
        userId = session['user_id']
    else:
        userId = False
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure category title was submitted
        if not request.form.get("title"):
            return apology("Please provide category title")
        elif not session["user_id"]:
            return apology("Anonymous users are not allowed to add categories")
        else:
            # add new category to database
            db.execute("INSERT INTO categories (category_title) VALUES (:title)",
                title=request.form.get("title"))

            currentCategories = db.execute("SELECT * FROM categories")

            # Show message
            return render_template("categories.html", showMessage=True, currentCategories=currentCategories, userId=userId)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        currentCategories = db.execute("SELECT * FROM categories")
        return render_template("categories.html", currentCategories=currentCategories, userId=userId)

@app.route('/category')
def category_route():
    id = request.args.get('id', default = 1, type = int)
    categoryName = db.execute("SELECT category_title FROM categories WHERE category_id=:id",
                            id=id)
    articles = db.execute("SELECT title, image, date, author_id, username, article_id FROM articles JOIN users ON users.id=articles.author_id WHERE category_id_article=:id",
                            id=id)
    currentCategories = db.execute("SELECT * FROM categories")
    return render_template("category.html", categoryName=categoryName[0]['category_title'], articles=articles, currentCategories=currentCategories)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Plesae provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide username", 403)
        else:
             # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))

            # Warn if username exists
            if len(rows) == 1:
                return apology("This username already exists. Please choose another.", 403)

        # Ensure password and confirmation were submitted
        if not request.form.get("password"):
            return apology("Please provide password", 403)
        elif not request.form.get("confirmation"):
            return apology("Please provide confirmation", 403)

        # Ensure password and confirmation match
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Password and confirmation do not match", 403)
        else:
            hash = generate_password_hash(request.form.get("password"))
            username = request.form.get("username")
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hash)

            # Redirect user to login page
            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
