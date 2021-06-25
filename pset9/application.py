import os
from cs50 import SQL
import datetime
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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


# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.globals.update(usd=usd)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    #select dictionary of transcations including symbol, name, sum shares bought by price point entered
    transactions = db.execute("SELECT symbol, name, SUM(shares) AS shares, price, SUM(total) AS Total FROM stocks WHERE userid = ? GROUP BY price, name;", session['user_id'])

    #query the cash balance and set cash as a the cash balance in USD form
    cash_balance = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
    cash = usd(cash_balance[0]['cash'])

    #query database for total invested and set total as cash + total invested in stocks
    total_invested = db.execute("SELECT SUM(total) AS total FROM stocks WHERE userid = ?", session['user_id'])
    invested = total_invested[0]['total']
    if invested == None:
        invested = 0
    total = usd(invested + cash_balance[0]['cash'])
    return render_template("index.html", transactions=transactions, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        shares = int(float(request.form.get("shares")))
        symbol = request.form.get("symbol")
        if not request.form.get("shares") or not request.form.get("symbol"):
            return apology("Invalid inputs", 400)
        if lookup(symbol) is None:
            return apology("Invalid ticker symbol", 400)
        if shares < 0 or type(shares) != int:
            return apology("Invalid Shares Input", 400)
        cash_balance = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        quote_dict = lookup(symbol)
        updated_cash = cash_balance[0]['cash'] - quote_dict['price'] * shares
        if updated_cash < 0:
            return apology("Insufficient Balance", 400)
        #If you have sufficient cash balance to purchase the stock at given price, then create new table that shows your stock holdings called stocks and insert into it purchase info
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, session['user_id'])
        db.execute("INSERT INTO stocks (userid, symbol, name, shares, price, total) VALUES (?, ?, ?, ?, ?, ?)",
        session['user_id'], quote_dict['symbol'], quote_dict['name'], shares, quote_dict['price'], quote_dict['price'] * shares)
        flash("Bought!")
        return redirect('/')
    if request.method == "GET":
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    #Create python dictionary that stores information on stocks purchased by session id uses
    history = db.execute("SELECT symbol, shares, price, transacted FROM stocks WHERE userid = ?", session['user_id'])
    return render_template("history.html", history=history)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not request.form.get("symbol"):
            return apology("must provide quote", 400)
        if lookup(symbol) == None:
            return apology("provide valid quote", 400)
        quote_info_dict = lookup(symbol)
        return render_template("quoted.html", quote_info_dict = quote_info_dict)
    if request.method == "GET":
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        existing_username = db.execute("SELECT username FROM users")
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif confirmation != password:
            return apology("passwords do not match", 400)
        for i in range(len(existing_username)):
            if username in existing_username[i]['username']:
                return apology("Username Already Exists", 400)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session['user_id'] = rows[0]['id']
        return redirect("/")
    elif request.method == "GET":
        return render_template("register.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form.get("username")
        currentp = request.form.get("currentpassword")
        newpassword = request.form.get("newpassword")
        newpasswordconfirm = request.form.get("newpasswordconfirm")

        if not username or not currentp or not newpassword or not newpasswordconfirm:
            return apology("Please Input Values!")

        #Check if username inputted does actually exist
        usernames = db.execute("SELECT username FROM users WHERE username = ?", username)
        if usernames[0]['username'] != username:
            return apology("Username does not exist")

        if newpassword != newpasswordconfirm:
            return apology("New Passwords Do not Match!")

        #Check if the password inputted matches the user's actual password
        rows = db.execute("SELECT hash FROM users WHERE username = ?", username)

        if not check_password_hash(rows[0]['hash'], currentp):
            return apology("Wrong Password")

        db.execute("UPDATE users SET hash = ? WHERE username = ?", generate_password_hash(newpassword), username)
        return render_template("login.html")

    if request.method == "GET":
        return render_template("reset_password.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        # initialize ticker sold and number of that stock sold
        ticker_sold = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        #if no input to either field output error
        if not ticker_sold:
            return apology("Choose a stock to sell")
        if not shares:
            return apology("Invalid Number of Shares")

        #Check if User has the shares to sell, query DB to return total amount of ticker share owned by session user
        rows = db.execute("SELECT SUM(shares) AS shares FROM stocks WHERE userid = ? GROUP BY ? HAVING shares > 0", session['user_id'], ticker_sold)
        if shares > rows[0]['shares']:
            return apology("Not enough shares to sell")

        #Create list of stocks owned to check if user altered the dropdown menu, if ticker sold is not in current stocks held return error
        stocks = db.execute("SELECT symbol FROM stocks WHERE userid = ? GROUP BY symbol HAVING SUM(shares) > 0", session['user_id'])
        if ticker_sold != stocks[0]['symbol']:
            return apology("Invalid Share Sold")

        #initialize variables for price, profit/loss, stocksold is a dict with name, price, symbol. cost_basis is the price at which the share sold.
        sell_info = lookup(ticker_sold)
        cost_basis = sell_info['price']
        gain = cost_basis * shares

        #set user cash balance to new balance
        cash_balance = db.execute("SELECT cash FROM users WHERE id = ?", session['user_id'])
        updated_cash = cash_balance[0]['cash'] + gain
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, session['user_id'])

        #update shares table that keeps track of transactions to print to history
        db.execute("INSERT INTO stocks (userid, symbol, name, shares, price, total) VALUES (?, ?, ?, ?, ?, ?)",
        session['user_id'], sell_info['symbol'], sell_info['name'], -1 * shares, sell_info['price'], -1*sell_info['price'] * shares)
        flash("Sold!")

        return redirect('/')

    if request.method == "GET":
        #render dropdown menu where each choice is ticker with positive amount of shares
        stocks = db.execute("SELECT symbol FROM stocks WHERE userid = ? GROUP BY symbol HAVING SUM(shares) > 0", session['user_id'])
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
