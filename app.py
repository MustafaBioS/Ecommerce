from flask import Flask, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Initialization

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

load_dotenv()
secret = os.getenv("secret_key")
app.config['SECRET_KEY'] = secret

db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Database

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(24), nullable=False)
    first_pic = db.Column(db.String(128), nullable=False)
    sec_pic = db.Column(db.String(128), nullable=False)
    third_pic = db.Column(db.String(128), nullable=False)

class Refunds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.Integer, nullable=False)

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)

# Routes

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/all')
def all():
    return render_template('all.html')

@app.route('/admin')
def admin():
    refunds = Refunds.query.all()
    messages = Messages.query.all()
    return render_template('admin.html', refunds=refunds, messages=messages)

@app.route('/message/view/<int:message_id>')
def view(message_id):
    message = Messages.query.filter_by(id=message_id).first()
    return render_template('view.html', message=message)

@app.route('/message/delete/<int:message_id>')
def delete_message(message_id):
    message = Messages.query.filter_by(id=message_id).first()
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for("admin"))

@app.route('/refund', methods=['POST'])
def refund():
    if request.method == 'POST':
        order = request.form.get('orderNum')
        phone = request.form.get('phoneNum')
        new_request = Refunds(order=order, phone=phone)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for("all"))

@app.route('/refund/delete/<int:refund_id>')
def delete_refund(refund_id):
    ref = Refunds.query.filter_by(id=refund_id).first()
    db.session.delete(ref)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('number')
        message = request.form.get('msg')
        new_msg = Messages(name=name, email=email, phone=phone, message=message)
        db.session.add(new_msg)
        db.session.commit()
        return redirect(url_for('all'))


# Run

if __name__ == '__main__':
    app.run(debug=True)