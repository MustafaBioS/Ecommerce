from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, send_from_directory, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_user, LoginManager
from dotenv import load_dotenv
import os
import uuid

# Initialization

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

load_dotenv()
secret = os.getenv("secret_key")
app.config['SECRET_KEY'] = secret

db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'profile'

# Database

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(24), nullable=False)
    price = db.Column(db.Float, nullable=False)
    first_pic = db.Column(db.String(128))
    sec_pic = db.Column(db.String(128))
    third_pic = db.Column(db.String(128))
    fourth_pic = db.Column(db.String(128))
    size_chart = db.Column(db.String(128))

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

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(36), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    size = db.Column(db.String(2), nullable=True)

    item = db.relationship("Items")

# Routes

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/all')
def all():
    products = Items.query.all()
    return render_template('all.html', products=products)

@app.route('/admin')
def admin():
    if current_user.is_admin:
        refunds = Refunds.query.all()
        messages = Messages.query.all()
        users = Users.query.all()
        products = Items.query.all()

        return render_template('admin.html', refunds=refunds, messages=messages, users=users, products=products)
    else:
        return redirect(url_for('home'))

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

@app.route("/products", methods=['POST'])
def product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        pics = request.files.getlist('pics[]')
        category = request.form.get('category')

        saved_filenames = []


        for pic in pics:
            if pic.filename != '':
                filename = pic.filename
                pic.save(f'uploads/{pic.filename}')
                saved_filenames.append(filename)

        titled = name.title()

        new_product = Items(name = titled,
            price = price, 
            quantity = quantity,
            category = category,
            first_pic = pics[0].filename if len(saved_filenames) > 0 else None,
            sec_pic = pics[1].filename if len(saved_filenames) > 1 else None,
            third_pic = pics[2].filename if len(saved_filenames) > 2 else None,
            fourth_pic = pics[3].filename if len(saved_filenames) > 3 else None,
            size_chart = pics[4].filename if len(saved_filenames) > 4 else None,)
        
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin'))
        
@app.route("/products/delete/<int:product_id>")
def delete_product(product_id):
    product = Items.query.filter_by(id=product_id).first()

    pics = [product.first_pic, product.sec_pic, product.third_pic, product.fourth_pic, product.size_chart]
    for pic in pics:
        if pic:
            path = os.path.join('uploads', pic)
            if os.path.exists(path):
                os.remove(path)

    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route("/product/view/<int:product_id>", methods=['GET', 'POST'])
def view_product(product_id):

    product = Items.query.filter_by(id=product_id).first()

    if request.method == 'GET':
        return render_template("product.html", product=product)

            

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

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "GET":
        return render_template("profile.html")
    if request.method == "POST":
        email = request.form.get("email")

        usersEmail = Users.query.filter_by(email=email).first()

        if email == "AdminEmail@gmail.com":
            if not usersEmail:
                user = Users(email=email, is_admin=True)
                db.session.add(user)
                db.session.commit()
            login_user(user)
            flash("Logged In As Admin!")
            return redirect(url_for('profile'))
        else:
            if not usersEmail:
                user = Users(email=email, is_admin=False)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('profile'))
            else:
                return redirect(url_for('profile'))
                
@app.route("/profile/delete/<int:profile_id>")
def profile_delete(profile_id):
    prof = Users.query.filter_by(id=profile_id).first()
    db.session.delete(prof)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory('uploads', filename)


@app.after_request
def set_guest_cookie(response):
    if current_user.is_authenticated:
        return response
    if not request.cookies.get("guest_id"):
        guest_id = str(uuid.uuid4())
        response.set_cookie("guest_id", guest_id, max_age=60*60*24*365*10)
    return response

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    user_id = get_current_user_id()

    if request.method == 'GET':
        cart_items = Cart.query.filter_by(uid=user_id).all()
        response = [
            {
                "id": c.item.id,
                "name": c.item.name,
                "price": c.item.price,
                "quantity": c.quantity,
                "pic": c.item.first_pic
            } for c in cart_items
        ]
        return render_template("cart.html", cart=response)

    if request.method == "POST":
        cart_data = request.json.get("cart", [])

        for entry in cart_data:
            item = Items.query.get(entry["id"])
            if not item:
                continue

            cart_row = Cart.query.filter_by(uid=user_id, item_id=item.id,size=entry.get("size")).first()
            if cart_row:
                cart_row.quantity += entry["quantity"]
            else:
                new_row = Cart(uid=user_id, item_id=item.id, quantity=entry["quantity"], size=entry.get("size"))
                db.session.add(new_row)

        db.session.commit()


        return jsonify({"status": "ok"})


def get_current_user_id():
    if current_user.is_authenticated:
        return f"user_{current_user.id}"
    return request.cookies.get("guest_id")

# Run

if __name__ == '__main__':
    app.run(debug=True)