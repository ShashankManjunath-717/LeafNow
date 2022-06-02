

#from crypt import methods
#from urllib import request
#from ast import With
#from unicodedata import name
#from pickle import GET
#from tkinter.tix import Select
from urllib import response
from flask.globals import request, session
from flask import Flask, redirect, render_template, request, flash, json,make_response
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, logout_user, login_manager, LoginManager, current_user
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import json
from flask_login import AnonymousUserMixin
import pdfkit
from flask_mail import Mail,Message


# mydatabase connection
local_server = True
app = Flask(__name__)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'leafnow001@gmail.com'
app.config['MAIL_PASSWORD'] = 'leafnow123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)
app.secret_key = "amrutha123"

# this is for getting the unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# app.config["SQLALCHEMY_DATABASE_URI"]='mysql://username:password@localhost/databasename'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/internship"
db = SQLAlchemy(app)


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


@login_manager.user_loader
def load_user(cust_id):
    return Customer.query.get(int(cust_id)) 

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    Phone_number = db.Column(db.Integer)
    email_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000), unique=True)

class donate(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sp = db.Column(db.String(100))
    date = db.Column(db.Date)


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":

        name = request.form.get('name')
        phone_number = request.form.get('mbno')
        email = request.form.get('email')
        password = request.form.get('pass')
        # print(email,name,phone_number,password)
        encpassword = generate_password_hash(password)
        custemail = Customer.query.filter_by(email_id=email).first()
        if custemail:
            flash("Email already registered", "warning")
            return render_template("usersignup.html")
        new_cust = db.engine.execute(
            f"INSERT INTO `customer` (`Name`,`Phone_number`,`email_id`,`password`) VALUES ('{name}','{phone_number}','{email}','{encpassword}')")
        flash("Sign Up Successfull! Please login", "Success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('pass')
        cust = Customer.query.filter_by(email_id=email).first()

        if cust and check_password_hash(cust.password, password):
            login_user(cust)
            flash("login Success ", "info")
            return render_template("booking.html")
        else:
            flash("Invalid login ", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))



@app.route("/test")
def test():

    try:
        a = Test.query.all()
        print(a)
        return f'my db is connected{a}'
    except Exception as e:
        print(e)
        return f'my db is not connected {e}'


@app.route('/logoutadmin')
def logoutadmin():
    session.pop('user')
    flash("Logout Successful", "warning")
    return redirect('/admin')

@app.route("/edetails", methods=['POST', 'GET'])
def edetails():
      return render_template("article.html")

@app.route("/donate", methods=['POST', 'GET'])
@login_required
def donate():
    if request.method == "POST":
        sp = request.form.get('SP')
        date = request.form.get('Date')
        print(sp,date)
        seed=db.engine.execute(
            f"INSERT INTO `donate` (`sp`,`date`) VALUES ('{sp}','{date}')")
        msg = Message('LEAF NOW', sender =  'leafnow001@gamil.com', recipients = [current_user.email_id])
            
        msg.body =  "Thanks for using Leaf Now! You can download your certificate using the below attachment"
            #msg.html = "<b>Hey Paul</b>, sending you this email from my <a href="https://google.com/%22%3EFlask app</a>, lmk if it works"
            
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
             #pdfkit.from_string(html, 'MyPDF.pdf', configuration=config)
        rendered=render_template('ticket.html',sp=sp,date=date)
        pdf=pdfkit.from_string(rendered,False,configuration=config)
        response=make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']='inline; filename=output.pdf'
            #return response
           
        msg.attach('donationdetails','application/pdf',pdf)
        mail.send(msg)
        flash("Ticket Booked!Check your Mail for the ticket","success")

   
            
    return render_template("booking.html")

app.run(debug=True)
