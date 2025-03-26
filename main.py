#pip install flask
from flask import Flask, render_template
import random as r

app = Flask(__name__)

@app.route("/login")
def index():
    return render_template("login.html")

@app.route("/home")
def drugi():
    slika = "https://www.opremisidom.com/wp-content/uploads/2023/03/20.84.1002.00_1800x1800.webp"
    return render_template("home.html", slika = slika)

app.run(debug = True)