from flask import Flask, render_template
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

# Database

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(24), nullable=False)
    first_pic = db.Column(db.String(128), nullable=False)
    sec_pic = db.Column(db.String(128), nullable=False)
    third_pic = db.Column(db.String(128), nullable=False)


# Routes

@app.route('/')
def home():
    return render_template("index.html")

# Run

if __name__ == '__main__':
    app.run(debug=True)