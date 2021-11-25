from flask import Flask, render_template, request, make_response, redirect, url_for, flash
import sqlalchemy
from yaml import load, Loader
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KEY'
globaluserid = 0

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
    global globaluserid
    username = request.form["username"]
    password = request.form["password"]

    # check if username and password combo exists SELECT count(*) FROM Users WHERE username = (%s) AND  password = (%s)
    sql1 = "SELECT * FROM Users WHERE username = \"{}\" AND password = \"{}\"".format(username, password)

    row = conn.execute(sql1).fetchone()
    if len(row) == 0:
        flash("NOPE", category='error')
        return redirect(url_for('chandrachur'))
    else:
        # pass userId to the food URL
        globaluserid = row[0]
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
        flash("NOPE", category='error')
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


@app.route('/users_foods', methods=['POST', 'GET'])
def users_foods():

    sql = "SELECT * FROM UsersFoods WHERE userId = (%s)"
    params = (globaluserid)
    all_data = conn.execute(sql, params).fetchall()

    return render_template("userFoods.html", users_foods=all_data)


@app.route('/users_exercises', methods=['POST', 'GET'])
def users_exercises():

    sql = "SELECT * FROM UsersExercises WHERE userId = (%s)"
    params = (globaluserid)
    all_data = conn.execute(sql, params).fetchall()

    return render_template("userExercises.html", users_exercises=all_data)


@app.route('/foodHistory', methods=['POST', 'GET'])
def foodHistory():

    sql = "SELECT * FROM UsersFoods NATURAL JOIN FoodHistory WHERE userId = (%s)"
    params = (globaluserid)
    all_data = conn.execute(sql, params).fetchall()

    return render_template("foodHistory.html", foodhists=all_data)


@app.route('/foodHistory_insert', methods=['POST'])
def foodHistory_insert():
    if request.method == 'POST':
        usersFoodsId = request.form['usersFoodsId']
        date = request.form['date']
        quantity = request.form['quantity']

        sql = "INSERT INTO FoodHistory (usersFoodsId, date, quantity) VALUES (%s, %s, %s)"
        params = (usersFoodsId, date, quantity)
        conn.execute(sql, params)

        flash("Food History Inserted Successfully", category='success')
        return redirect(url_for('foodHistory'))


@app.route('/foodHistory_update', methods=['GET', 'POST'])
def foodHistory_update():
    if request.method == 'POST':

        foodHistoryId = request.form.get('foodHistoryId')
        newusersFoodsId = request.form['usersFoodsId']
        newdate = request.form['date']
        newquantity = request.form['quantity']

        sql = "UPDATE FoodHistory SET usersFoodsId = (%s), date = (%s), quantity = (%s) WHERE foodHistoryId = (%s)"
        params = (newusersFoodsId, newdate, newquantity, foodHistoryId)
        conn.execute(sql, params)

        flash("Food History Updated Successfully", category='success')
        return redirect(url_for('foodHistory'))


@app.route('/foodHistory_delete/<foodHistoryId>/', methods=['GET', 'POST'])
def foodHistory_delete(foodHistoryId):
    sql = "DELETE FROM FoodHistory WHERE foodHistoryId = (%s)"
    params = (foodHistoryId)
    conn.execute(sql, params)

    flash("Food History Deleted Successfully", category='success')
    return redirect(url_for('foodHistory'))


@app.route('/exerciseHistory', methods=['POST', 'GET'])
def exerciseHistory():

    sql = "SELECT * FROM UsersExercises NATURAL JOIN ExerciseHistory WHERE userId = (%s)"
    params = (globaluserid)
    all_data = conn.execute(sql, params).fetchall()

    return render_template("exerciseHistory.html", exhists=all_data)


@app.route('/exerciseHistory_insert', methods=['POST'])
def exerciseHistory_insert():
    if request.method == 'POST':
        usersExercisesId = request.form['usersExercisesId']
        date = request.form['date']
        duration = request.form['duration']

        sql = "INSERT INTO ExerciseHistory (usersExercisesId, date, duration) VALUES (%s, %s, %s)"
        params = (usersExercisesId, date, duration)
        conn.execute(sql, params)

        flash("Exercise History Inserted Successfully", category='success')
        return redirect(url_for('exerciseHistory'))


@app.route('/exerciseHistory_update', methods=['GET', 'POST'])
def exerciseHistory_update():
    if request.method == 'POST':

        exerciseHistoryId = request.form.get('exerciseHistoryId')
        newusersExercisesId = request.form['usersExercisesId']
        newdate = request.form['date']
        newduration = request.form['duration']

        sql = "UPDATE ExerciseHistory SET usersExercisesId = (%s), date = (%s), duration = (%s) " \
              "WHERE exerciseHistoryId = (%s)"
        params = (newusersExercisesId, newdate, newduration, exerciseHistoryId)
        conn.execute(sql, params)

        flash("Exercise History Updated Successfully", category='success')
        return redirect(url_for('exerciseHistory'))


@app.route('/exerciseHistory_delete/<exerciseHistoryId>/', methods=['GET', 'POST'])
def exerciseHistory_delete(exerciseHistoryId):
    sql = "DELETE FROM ExerciseHistory WHERE exerciseHistoryId = (%s)"
    params = (exerciseHistoryId)
    conn.execute(sql, params)

    flash("Exercise History Deleted Successfully", category='success')
    return redirect(url_for('exerciseHistory'))


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