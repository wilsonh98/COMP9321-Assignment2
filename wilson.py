# Housing Prices API

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn import metrics
from flask import Flask, send_file, make_response
from flask import request
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
import base64
import json
from time import time
from functools import wraps
import flask_profiler


SECRET_KEY = "A SECRET AND VERY LONG RANDOM STRING USED AS KEY"
expires_in = 600

app = Flask(__name__)
api = Api(app, default="Housing", title="Melbourne Dataset", description="<description here>")

# https://github.com/muatik/flask-profiler
app.config["flask_profiler"] = {
    "enabled": app.config["DEBUG"], 
    "storage": {
        "engine": "sqlite"
    },
    "ignore": [
        "^/static/.*"
    ]
}

# def get_crime_graph(suburb):
# upload_parser = api.parser()
# upload_parser.add_argument('file', location='files',
#                            type=FileStorage, required=True)

@api.route('/crimes/timeline/<string:suburb>')
@api.representation('image/png')
class Crime_Timeline(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("Suburb is: ", suburb)

        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )

        bytes_obj = crime_timeline(suburb)
        return bytes_obj
        # return send_file(bytes_obj, mimetype='image/png')

@api.route('/prediction/<distance>')
# @api.route('/prediction/<float:distance>')
class Price_Prediction(Resource):
    def get(self, distance):
        try: 
            distance = float(distance)
        except ValueError:
            api.abort(400, "Not a valid input")
        if distance > 35 or distance < 0:
            api.abort(400, 'Distance is outside of CBD prediction')
        price = str(round(price_prediction(dist=distance), 2)) 
        price = "$" + price
        return {"Price": price}   

# In order to active flask-profiler, you have to pass flask
# app as an argument to flask-profiler.
# All the endpoints declared so far will be tracked by flask-profiler.
flask_profiler.init_app(app)


# endpoint declarations after flask_profiler.init_app() will be
# hidden to flask_profiler.


def price_prediction(dist=2.5, prop_type="h"):
    print(dist)
    df = pd.read_csv('melb_data.csv')
    df = df[(df['Rooms'] >= 2) & (df['Rooms'] <= 4) & (df["Type"] == prop_type)]
    df = df[(df.Price < np.percentile(df.Price,98)) & (df.Price > np.percentile(df.Price,2)) ]
    df = df[["Distance", "Price"]]
    X = df.iloc[:, :-1].values
    y = df.iloc[:, 1].values
    regressor = linear_model.LinearRegression()
    regressor.fit(X,y)
    ds = [[dist]]
    y_pred = regressor.predict(ds)
    return y_pred[0]    

def crime_timeline(suburb="abbotsford"):
    df = pd.read_csv('crime.csv', dtype={"Incidents Recorded": str})
    df['Incidents Recorded'] = df['Incidents Recorded'].replace(',','', regex=True)
    df['Incidents Recorded'] = pd.to_numeric(df['Incidents Recorded'])
    df = df[(df['Suburb/Town Name'] == suburb)]
    df = df[['Year ending September', 'Incidents Recorded']]
    df.columns = ['Year', 'Count']
    df = df.groupby(['Year']).sum()
    df.plot(kind='line',y='Count',color='red', title="Crime timeline of " + suburb)
    # img = io.StringIO()
    # plt.savefig(img, format='png')
    # plt.close()
    # img.seek(0)
    dictdf = df.to_dict()
    # plot_url = base64.b64encode(img.getvalue())
    return dictdf

if __name__ == "__main__":
    crime_df = pd.read_csv("crime.csv", dtype={"Incidents Recorded": str})
    app.run(debug=True)