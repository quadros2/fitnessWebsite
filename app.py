from flask import Flask

app = Flask(__name__)


@app.route('/')
def chandrachur():
    return 'Shrirang goofy as hell bruh no cap'