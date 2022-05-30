# 100 Days of Code Capstone Project
# Online shop with payment system

import os

import stripe
from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

YOUR_DOMAIN = "http://127.0.0.1:5000"
stripe_cart = []
web_cart = []
stripe.api_key = os.environ.get("STRIPE_API")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Connect to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
Bootstrap(app)
db = SQLAlchemy(app)

# User secure login
# login_manager = LoginManager()
# login_manager.init_app(app)

# Table Configuration
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.INTEGER, primary_key=True)
    email = db.Column(db.VARCHAR(100), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(32), nullable=False)


class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR(50), nullable=False)
    description = db.Column(db.VARCHAR(200), nullable=False)
    image_path = db.Column(db.VARCHAR(200), nullable=False)
    cost = db.Column(db.VARCHAR(10), nullable=False)
    api_id = db.Column(db.VARCHAR(50), nullable=False)


class ItemForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    description = StringField("Item Description", validators=[DataRequired()])
    image_path = StringField("Item ImagePath", validators=[DataRequired()])
    cost = StringField("Item Cost", validators=[DataRequired()])
    api_id = StringField("Stripe API ID", validators=[DataRequired()])
    submit = SubmitField("Submit")


# ORDER HISTORY TABLE
# ID
# customer email
# item
# cost


# Create initial database
# db.create_all()

# Webpage routes
@app.route("/")
def home():
    all_items = db.session.query(Item).all()
    return render_template("index.html", item_list=all_items)


@app.route("/cart")
def cart():
    return render_template("cart.html", web_cart=web_cart)


@app.route("/add-to-cart/<int:item_id>", methods=["GET", "POST"])
def add_to_cart(item_id):
    item_to_add = Item.query.get(item_id)
    api_id = item_to_add.api_id
    image_path = item_to_add.image_path
    name = item_to_add.name
    cost = item_to_add.cost
    stripe_cart.append({"price": api_id, "quantity": 1})
    web_cart.append({"image_path": image_path, "name": name, "cost": cost})
    print(stripe_cart, web_cart)  # TESTING
    return redirect(url_for("home"))


@app.route("/clear-cart", methods=["GET", "POST"])
def clear_cart():
    global stripe_cart, web_cart
    stripe_cart = []
    web_cart = []
    print(stripe_cart, web_cart)  # TESTING
    return redirect(url_for("cart"))


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    if stripe_cart != []:
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=stripe_cart,
                mode="payment",
                success_url=YOUR_DOMAIN + "/success",
                cancel_url=YOUR_DOMAIN + "/cancel",
            )
        except Exception as e:
            return str(e)

        return redirect(checkout_session.url, code=303)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancel")
def cancel():
    return render_template("cancel.html")


# LOGIN PAGE

# ITEM PAGE

# ADMIN PAGE
@app.route("/additem", methods=["GET", "POST"])
def add_item():
    all_items = db.session.query(Item).all()
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            description=form.description.data,
            image_path=form.image_path.data,
            cost=form.cost.data,
            api_id=form.api_id.data,
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("additem.html", form=form, item_list=all_items)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
