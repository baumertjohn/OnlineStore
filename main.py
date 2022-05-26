# 100 Days of Code Capstone Project
# Online shop with payment system

import os

import stripe
from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

YOUR_DOMAIN = "http://127.0.0.1:5000"
stripe.api_key = os.environ.get("STRIPE_API")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Connect to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
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
    name = StringField("Item Name", validators=[DataRequired])
    description = StringField("Item Description", validators=[DataRequired])
    image_path = StringField("Item ImagePath", validators=[DataRequired])
    cost = StringField("Item Cost", validators=[DataRequired])
    api_id = StringField("Stripe API ID", validators=[DataRequired])
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
    return render_template("index.html")


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": "price_1L2oJ4CTsjrSmP7yi7pO7J7W",
                    "quantity": 1,
                },
                {
                    "price": "price_1L3StoCTsjrSmP7ylLlmGPbt",
                    "quantity": 1,
                },
            ],
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
@app.route("/additem")
def add_item():
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
    return render_template("additem.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
