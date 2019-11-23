#!/usr/bin/python3

from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/details/<action>', methods=["GET", "POST"])
def details(action):
    if (action == "buy"):
        return render_template("buyer.html")
    elif (action == "sell"):
        return render_template("seller.html")
    else:
        pass

@app.route("/buyer")
def buyer():
    return render_template("buyer.html")

@app.route("/seller")
def seller():
    return render_template("seller.html")


@app.route("/crime")
def crime():
    return render_template("crime.html")


@app.route("/houses")
def houses():
    return render_template("houses.html")


@app.route("/schools", methods=["GET","POST"])
def schools():
    if (request.method == "POST"):
        query = request.form['suburb']
        
    return render_template("schools.html")


app.run(debug=True, port=8000)
