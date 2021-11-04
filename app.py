from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://calcount:mongodb99@calcount-328016:us-central1:calcount/calCount"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Food(db.Model):
    food_id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(100), nullable=False)
    calories = db.Column(db.Integer, nullable=False)

    def __init__(self, food_name, calories):
        self.food_name = food_name
        self.calories = calories

@app.route('/food')
def food():
    all_data = Food.query.all()
    return render_template("food.html", foods=all_data)

@app.route('/')
def chandrachur():
    return render_template("menu.html")

if __name__ == "__main__":
    app.run(debug=True)