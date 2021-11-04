from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from yaml import load, Loader
import os
import pymysql

app = Flask(__name__)


def init_connect_engine():
    if os.environ.get('GAE_ENV') != 'standard':
        variables = load(open("app.yaml"), Loader=Loader)
        env_variables = variables['env_variables']
        for var in env_variables:
            os.environ[var] = env_variables[var]

    pool = sqlalchemy.create_engine(

        sqlalchemy.engine.url.URL(
            drivername="mysql+pymysql",
            username=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DB'),
            host=os.environ.get('MYSQL_HOST')  # ip
        )
    )
    return pool

engine = init_connect_engine()

conn = engine.connect()

# app.config["SECRET_KEY"] = "yoursecretkey"
# app.config["SQLALCHEMY_DATABASE_URI"]= "mysql+pymysql://root:mongodb99@35.223.231.139/calCount"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)


@app.route('/food')
def food():
    # all_data = Food.query.all()
    all_data = conn.execute("SELECT * FROM Food;").fetchall()
    return render_template("food.html", foods=all_data)


@app.route('/food_insert', methods=['POST'])
def food_insert():
    # haven't written functionality yet
    return


@app.route('/food_update', methods=['GET', 'POST'])
def food_update():
    # haven't written functionalty yet
    return


@app.route('/food_delete/<foodId>/', methods=['GET', 'POST'])
def food_delete(foodId):
    #haven't written functionality yet
    return


@app.route('/')
def chandrachur():
    return render_template("menu.html")

if __name__ == "__main__":
    app.run(debug=True)