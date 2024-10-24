from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from models.models import *
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = "somesupersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:edykab@localhost/esolution_db'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

# Create all tables
Base.metadata.create_all(engine)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    if 'loggedin' in session:
        # Fetch recent expenses and incomes for dashboard
        with engine.connect() as con:
            expenses = con.execute(
                text(f"SELECT * FROM expense WHERE user_id = {session['id']} ORDER BY date DESC LIMIT 5")
            ).fetchall()
            incomes = con.execute(
                text(f"SELECT * FROM income WHERE user_id = {session['id']} ORDER BY date DESC LIMIT 5")
            ).fetchall()
        return render_template('home.html', username=session['username'], expenses=expenses, incomes=incomes)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username'].lower()
        password_entered = request.form['password']
        
        # Encrypt the password
        hash = password_entered + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()
        
        # Check if user exists
        with engine.connect() as con:
            result = con.execute(
                text("SELECT * FROM user WHERE username = :username AND password = :password"),
                {"username": username, "password": password}
            )
            account = result.fetchone()
            
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            msg = "Logged in successfully"
            return redirect(url_for('home', msg=msg))
        else:
            msg = "Incorrect username/password"
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        username = request.form['username'].lower()
        cusername = request.form['cusername'].lower()
        password = request.form['password']
        cpassword = request.form['cpassword']
        
        if username != cusername:
            msg = "Usernames do not match"
            return render_template('register.html', msg=msg)
            
        if password != cpassword:
            msg = "Passwords do not match"
            return render_template('register.html', msg=msg)
            
        with engine.connect() as con:
            result = con.execute(
                text("SELECT * FROM user WHERE username = :username"),
                {"username": username}
            )
            account = result.fetchone()
            
        if account:
            msg = "Account already exists"
            return render_template('register.html', msg=msg)
            
        if not username or not password:
            msg = "Please fill out the form"
            return render_template('register.html', msg=msg)
            
        # Encrypt password and insert user
        hash = password + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()
        
        with engine.connect() as con:
            con.execute(
                text("INSERT INTO user (username, password) VALUES (:username, :password)"),
                {"username": username, "password": password}
            )
            con.commit()
            
        msg = "Account created successfully"
        return redirect(url_for('login', msg=msg))
        
    return render_template('register.html', msg=msg)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        
        with engine.connect() as con:
            con.execute(
                text("INSERT INTO expense (user_id, date, description, amount, category) "
                     "VALUES (:user_id, :date, :description, :amount, :category)"),
                {
                    "user_id": session['id'],
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "category": category
                }
            )
            con.commit()
        return redirect(url_for('expenses'))
    
    # Fetch existing expenses
    with engine.connect() as con:
        expenses = con.execute(
            text("SELECT * FROM expense WHERE user_id = :user_id ORDER BY date DESC"),
            {"user_id": session['id']}
        ).fetchall()
    return render_template('expenses.html', expenses=expenses)

@app.route('/income', methods=['GET', 'POST'])
def income():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        date = request.form['date']
        source = request.form['source']
        amount = request.form['amount']
        
        with engine.connect() as con:
            con.execute(
                text("INSERT INTO income (user_id, date, source, amount) "
                     "VALUES (:user_id, :date, :source, :amount)"),
                {
                    "user_id": session['id'],
                    "date": date,
                    "source": source,
                    "amount": amount
                }
            )
            con.commit()
        return redirect(url_for('income'))
    
    # Fetch existing income entries
    with engine.connect() as con:
        incomes = con.execute(
            text("SELECT * FROM income WHERE user_id = :user_id ORDER BY date DESC"),
            {"user_id": session['id']}
        ).fetchall()
    return render_template('income.html', incomes=incomes)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)