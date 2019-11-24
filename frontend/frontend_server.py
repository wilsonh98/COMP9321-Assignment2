#!/usr/bin/python3

import requests
from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)

URL = "http://127.0.0.1:5000/"

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route("/result/<ans>")
def result(ans):
    return render_template("result.html", arg=ans)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        distance = request.form['distance']
        d = float(distance)
        t = request.form['type']
        print(d)
        url = URL + "prediction/" + distance
        if t:
            url = url + "?prop_type=" + t
        
        r = requests.get(url)
        r = r.json()['Price']
        return redirect(url_for("result", ans=str(r)))

    return render_template("predict.html")


@app.route("/avgprice", methods=["GET", "POST"])
def avg_price():
    if request.method == "POST":
        suburb = request.form['suburb']
        url = URL + "suburbs/averagePrice/" + suburb
        r = requests.get(url)
        return redirect(url_for("result", ans=str(r.json())))
    return render_template("avgPrice.html")


@app.route("/schools", methods=["GET","POST"])
def schools():
    if (request.method == "POST"):
        q = request.form['council']
        avg = request.form.get("average")
        url = URL + "schools/ranking/" + q
        if avg:
            url = url + "?average=1"
        
        r = requests.get(url)
        return redirect(url_for("result", ans=str(r.json())))
        
    return render_template("schools.html")


@app.route("/crime")
def crime():
    return render_template("crime.html")


@app.route("/houses")
def houses():
    return render_template("houses.html")





app.run(debug=True, port=8000)
