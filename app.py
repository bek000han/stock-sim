import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

app = Flask(__name__)

app.jinja_env.filters["usd"] = usd

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///finance.db")

# export API_KEY=pk_e5ff8d74ea0745b69a73d3c0ac0dd2c6
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    try:
        userid = session["user_id"]
        values = db.execute(f"SELECT symbol, sum(shares), price, name FROM transactions WHERE userid = {userid} GROUP BY symbol ORDER BY symbol ASC")
        for i in range(len(values)):
            values[i]["price"] = lookup(values[i]["symbol"])["price"]
        funds = db.execute(f"SELECT cash FROM users WHERE id = {userid}")
        total = funds[0]["cash"]
        for i in range(len(values)):
            total += float(values[i]["price"]) * float(values[i]["sum(shares)"])
        return render_template("/index.html", values=values, funds=funds, total=round(total, 2))
    except TypeError:
        return apology("IEX Cloud API key has expired, please renew.", "login.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    thispage = "buy.html"
    try:
        if request.method == "POST":
            shares = int(request.form.get("shares"))
            symbol = request.form.get("symbol")
            price = lookup(symbol.lower())["price"]
            name = lookup(symbol.lower())["name"]
            time = datetime.now()
            userid = session["user_id"]
            funds = db.execute(f"SELECT cash FROM users WHERE id = {userid}")
            if not symbol or not shares:
                return apology("Missing values.", thispage)
            if shares < 1:
                return apology("Invalid shares amount.", thispage)
            if funds[0]["cash"] < (shares * price):
                return apology("Insufficient funds.", thispage)
            else:
                symbol = symbol.upper()
                db.execute("INSERT INTO transactions(time, shares, price, userid, symbol, name) VALUES(?, ?, ?, ?, ?, ?)",
                            time, shares, price, userid, symbol, name)
                paid = float(funds[0]["cash"]) - (shares * price)
                db.execute(f"UPDATE users SET cash = {paid} WHERE id = {userid}")
                flash("Bought!")
                return redirect("/")
        else:
            return render_template("/buy.html")
    except TypeError:
        return apology("Invalid input type.", thispage)
    except ValueError:
        return apology("Invalid number, only integers.", thispage)


@app.route("/history")
@login_required
def history():
    userid = session["user_id"]
    values = db.execute(f"SELECT symbol, shares, price, time FROM transactions WHERE userid = {userid} ORDER BY time DESC")
    return render_template("/history.html", values=values)


@app.route("/login", methods=["GET", "POST"])
def login():
    thispage = "login.html"
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Must provide username.", thispage)
        elif not request.form.get("password"):
            return apology("Must provide password.", thispage)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password.", thispage)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    thispage = "quote.html"
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Missing symbol.", thispage)
        else:
            stock = lookup(request.form.get("symbol").lower())
            print(stock)
            if stock != None:
                return render_template("quoted.html", stock=stock)
            else:
                return apology("Invalid symbol.", thispage)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    thispage = "register.html"
    usernames = db.execute("SELECT username FROM users")
    username = request.form.get("username")
    password = request.form.get("password")
    chars = "1234567890"
    special = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
    usernameslist = []
    for i in range(len(usernames)):
        usernameslist = usernames[i]["username"]
    try:
        if request.method == "POST":
            if not username:
                return apology("Must provide username.", thispage)
            elif username in usernameslist:
                return apology("Username already exists.", thispage)
            elif not password:
                return apology("Must provide password.", thispage)
            elif not (password == request.form.get("confirmation")):
                return apology("Passwords do not match.", thispage)
            elif (len(password) < 7) or (len(password) > 20):
                return apology("Password of invalid length.", thispage)
            elif not (any((c in chars) for c in password) and any((c in special) for c in password)):
                return apology("Password must contain numbers and symbols.", thispage)
            else:
                hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
                db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, hash)
                return redirect("/login")
        else:
            return render_template("register.html")
    except ValueError:
        return apology("Username already exists.", thispage)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    userid = session["user_id"]
    options = db.execute(f"SELECT symbol FROM transactions WHERE userid = {userid} GROUP BY symbol ORDER BY symbol ASC")
    thispage = "sell.html"

    if request.method == "POST":
        shares = int(request.form.get("shares"))
        if request.form.get("symbol") == None:
            return apology("Invalid symbol.", thispage)
        symbol = "'"+request.form.get("symbol")+"'"
        values = db.execute(f"SELECT symbol, sum(shares) FROM transactions WHERE userid = {userid} AND symbol = {symbol} GROUP BY symbol")
        if not shares:
            return apology("Must provide shares.", thispage)
        if values[0]["sum(shares)"] < int(shares):
            return apology("Not enough shares owned.", thispage)
        else:
            shares = -abs(shares)
            symbol = request.form.get("symbol")
            price = lookup(symbol.lower())["price"]
            name = lookup(symbol.lower())["name"]
            time = datetime.now()
            funds = db.execute(f"SELECT cash FROM users WHERE id = {userid}")
            db.execute("INSERT INTO transactions(time, shares, price, userid, symbol, name) VALUES(?, ?, ?, ?, ?, ?)",
                        time, shares, price, userid, symbol, name)
            paid = float(funds[0]["cash"]) + (abs(shares) * price)
            db.execute(f"UPDATE users SET cash = {paid} WHERE id = {userid}")
            flash("Sold!")
            return redirect("/")
    else:
        return render_template("sell.html", options=options)
