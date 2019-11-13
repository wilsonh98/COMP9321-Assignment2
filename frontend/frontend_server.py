#!/usr/bin/python3

from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)
app.run(debug=True, port=5000)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/details/<action>', methods=["GET", "POST"])
def details(action):
    if (action == "buy"):
        return render_template("buyer.html")
    elif (action == "sell"):
        return render_template("seller.html")
    else:
        return "Error"
