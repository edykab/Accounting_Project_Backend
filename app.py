from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from models.models import *
import hashlib

app = Flask(__name__)
app.secret_key="somesupersecretkey"
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://root:edykab247@localhost/accounting_data'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

Base.metadata.create_all(engine)

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST'and 'email' in request.form and 'password' in request.form:

        # Get form data
        email = request.form['email']
        password = request.form['password']

        #decrypt the password
        hash = password + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()

        #check if the user exists in the database
        with engine.connect() as con:
            result = con.execute(text(f"Select * from user where email = '{email}' and password = '{password}'"))
            account = result.fetchone()
            con.commit()

        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['email'] = account.email
            msg = "Logged in successfully"
            return redirect(url_for('dashboard', msg=msg))
        else:
            msg = "Incorrect email/password"
    return render_template('login.html', msg=msg)   
       


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg =""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        #get the form values
        username = request.form['username'].lower()
        email = request.form['email']
        password = request.form['password']
       
        with engine.connect() as con:
            result = con.execute(text(f"Select * from user where username = '{username}'"))
            account = result.fetchone()
            con.commit()
        if account:
            msg = "Account already exists"
            return render_template('register.html', msg=msg)
        
        if not username or not password or not email:
                msg = "Please fill out the form"
                return render_template('register.html', msg=msg)
        else:
            #encrypt the password
            hash = password + app.secret_key
            hash = hashlib.sha256(hash.encode())
            password = hash.hexdigest()
            #insert the user into the database
            with engine.connect() as con:
                con.execute(text(f"Insert into user (username, password, email) values ('{username}', '{password}', '{email}')"))
                con.commit()
            msg = "Account created successfully"
            return redirect(url_for('login', msg=msg))
    return render_template('register.html', msg=msg)




@app.route('/dashboard')  
def dashboard():

    # Check if user is logged in
    if 'loggedin' not in session: 
        return redirect(url_for('login'))

    user_id = session['id']

    # Query for user from database
    User = User.query.get(user_id) 

    # Get user's expenses and income
    expenses = Expenses.query.filter_by(user_id=user_id)  
    income = Income.query.filter_by(user_id=user_id)

    # Aggregate totals 
    expenses_total = session.query(func.sum(Expenses.amount)).filter(Expenses.user_id == user_id).scalar()   
    income_total = session.query(func.sum(Income.amount)).filter(Income.user_id == user_id).scalar()

    # Render dashboard page 
    return render_template('dashboard.html', expenses=expenses, 
                           income=income,
                           expenses_total=expenses_total,
                           income_total=income_total)


@app.route('/add_expenses', methods=['POST'])
def add_expenses():
    # Extract form data
    date = request.form.get('date')
    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    category = request.form.get('category')

    # Add expenses to the database
    expenses = Expenses(user_id=session['id'], date=date, description=description, amount=amount, category=category)
    session.add(expenses)
    session.commit()

    # Redirect back to the dashboard
    return redirect(url_for('dashboard'))

@app.route('/add_income', methods=['POST'])
def add_income():
    # Extract form data
    date = request.form.get('date')
    source = request.form.get('source')
    amount = float(request.form.get('amount'))

    # Add income to the database
    income = Income(user_id=session['id'], date=date, source=source, amount=amount)
    session.add(income)
    session.commit()

    # Redirect back to the dashboard
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
