from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from yaml import load, Loader
import os
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KEY'

#lloyd
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
#chan
@app.route('/food', methods=['POST', 'GET'])
def food():
    #grabbing parameters from login page
    username = request.args.get('username')
    password = request.args.get('password')

    all_data = conn.execute("SELECT * FROM Food;").fetchall()
    return render_template("food.html", foods=all_data)

#search is also chan

#ben
@app.route('/food_insert', methods=['POST'])
def food_insert():
    if request.method == 'POST':
        foodName = request.form['foodName']
        calories = request.form['calories']

        sql = "INSERT INTO Food (foodName, calories) VALUES (%s, %s)"
        params = (foodName, calories)
        conn.execute(sql, params)

        flash("Food Inserted Successfully", category='success')
        return redirect(url_for('food'))

#ben
@app.route('/food_update', methods=['GET', 'POST'])
def food_update():
    if request.method == 'POST':

        foodId = request.form.get('foodId')
        newfoodName = request.form['foodName']
        newcalories = request.form['calories']

        sql = "UPDATE Food SET foodName = (%s), calories = (%s) WHERE foodId = (%s)"
        params = (newfoodName, newcalories, foodId)
        conn.execute(sql, params)

        flash("Food Updated Successfully", category='success')
        return redirect(url_for('food'))


#ben
@app.route('/food_delete/<foodId>/', methods=['GET', 'POST'])
def food_delete(foodId):
    sql = "DELETE FROM Food WHERE foodId = (%s)"
    params = (foodId)
    conn.execute(sql, params)

    flash("Food Deleted Successfully", category='success')
    return redirect(url_for('food'))

#shrirang
@app.route('/totalCals')
def totalCals():

    sql = "SELECT firstName, lastName, date, SUM(fh.quantity * f.calories) as totalCals " \
          "FROM FoodHistory fh NATURAL JOIN UsersFoods uf NATURAL JOIN Users u NATURAL JOIN Food f " \
          "GROUP BY userId, firstName, lastName, date " \
          "ORDER BY firstName, lastName"


    all_data = conn.execute(sql).fetchall()
    return render_template("totalCals.html", totals=all_data)

#shrirang
@app.route('/totalBurned')
def totalBurned():

    sql = "SELECT firstName, lastName, date, SUM(duration * caloriesBurned) as totalBurned " \
          "FROM ExerciseHistory eh NATURAL JOIN UsersExercises ue NATURAL JOIN Users u NATURAL JOIN Exercise e " \
          "GROUP BY userId, firstName, lastName, date " \
          "ORDER BY firstName, lastName"

    all_data = conn.execute(sql).fetchall()
    return render_template("totalBurned.html", totals=all_data)

@app.route('/login', methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    # check if username and password combo exists SELECT count(*) FROM Users WHERE username = (%s) AND  password = (%s)
    sql1 = "SELECT * FROM Users WHERE username = \"{}\" AND password = \"{}\"".format(username, password)
    if len(conn.execute(sql1).fetchall()) == 0:
        flash("NOPE", category='success')
        return redirect(url_for('chandrachur'))
    else:
        #pass username and password params to the food URL
        return redirect(url_for('renderMain'))
    
@app.route('/signup', methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    firstName = request.form["firstName"]
    lastName = request.form["lastName"]
    calorieTarg = request.form["calorieTarg"]

    # check if username exists
    sql1 = "SELECT * FROM Users WHERE username = \"{}\"".format(username)
    if len(conn.execute(sql1).fetchall()) == 1:
        flash("NOPE")
        return redirect(url_for('rendersignup'))
    
    #create a unique userid using newUserId = max(userId) + 1
    sql2 = "SELECT MAX(userId) FROM Users"
    maxUserIdDict = {}
    maxUserId = conn.execute(sql2)
    for rowproxy in maxUserId:
        for column, value in rowproxy.items():
            # build up the dictionary
            maxUserIdDict[column] = value
    newMaxUserId = maxUserIdDict['MAX(userId)'] + 1

    #insert new user in user table with given credentials
    sql3 = "INSERT INTO Users VALUES ({}, \"{}\", \"{}\", \"{}\", \"{}\", {})".format(newMaxUserId, username, password, firstName, lastName, calorieTarg)
    conn.execute(sql3)
    
    flash("success!")
    return redirect(url_for('/renderMain'))


@app.route('/rendersignup', methods=["POST"])
def rendersignup():
    return render_template("signup.html")

@app.route('/renderMain')
def renderMain():
    return render_template("menu.html")
    
@app.route('/', methods=["POST", "GET"])
def chandrachur():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)