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
import werkzeug
from time import time
from functools import wraps
from flask_profiler import Profiler
import flask_monitoringdashboard as dashboard

SECRET_KEY = "A SECRET AND VERY LONG RANDOM STRING USED AS KEY"
expires_in = 600

app = Flask(__name__)
api = Api(app, default="Housing", title="Melbourne Dataset", description="<description here>")


dashboard.bind(app)

<<<<<<< HEAD
# file_upload = reqparse.RequestParser()
# file_upload.add_argument('image', location='files',
#                            type=werkzeug.datastructures.FileStorage, required=True, help="PNG Image")
parser = reqparse.RequestParser()
=======
>>>>>>> 137b05d364eacf4cea6e61ab77e70b46120e8f1d

@api.route('/crimes/timeline/<string:suburb>')
class Crime_Timeline(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("Suburb is: ", suburb)
        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )
<<<<<<< HEAD
        # args = file_upload.parse_args()
        # if args['image'].mimetype == 'image/png':
        #     args['image'].save(crime_timeline(suburb))
        # else:
        #     abort(404)

=======
        
>>>>>>> 137b05d364eacf4cea6e61ab77e70b46120e8f1d
        return crime_timeline(suburb)

@api.route('/prediction/<distance>', defaults={"prop_type": "h"})
@api.route('/prediction/<distance>/<string:prop_type>')
# @api.route('/prediction/<float:distance>')
class Price_Prediction(Resource):
<<<<<<< HEAD
    def get(self, distance):
        try:
=======
    def get(self, distance, prop_type):
        try: 
>>>>>>> 137b05d364eacf4cea6e61ab77e70b46120e8f1d
            distance = float(distance)
        except ValueError:
            api.abort(400, "Not a valid input")
        if distance > 35 or distance < 0:
            api.abort(400, 'Distance is outside of CBD prediction')
<<<<<<< HEAD
        price = str(round(price_prediction(dist=distance), 2))
        price = "$" + price
        return {"Price": price}
=======
        if (prop_type == "h" or prop_type == "u" or prop_type == "t"):
            price = str(round(price_prediction(dist=distance, prop_type=prop_type), 2)) 
            price = "$" + price
            return {"Price": price}   
        else:
            api.abort(400, 'Property Type is not valid (h, t, u)')
>>>>>>> 137b05d364eacf4cea6e61ab77e70b46120e8f1d


def price_prediction(dist, prop_type="h"):
    print(prop_type)
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
    output = io.BytesIO()
    plt.savefig(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    crime_df = pd.read_csv("crime.csv", dtype={"Incidents Recorded": str})
    app.run(debug=True)