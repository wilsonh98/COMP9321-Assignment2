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
    "basicAuth":{
        "enabled": True,
        "username": "admin",
        "password": "admin"
    },
    "ignore": [
        "^/static/.*"
    ]
}

profiler = Profiler()  # You can have this in another module
profiler.init_app(app)
# Or just Profiler(app)

# file_upload = reqparse.RequestParser()
# file_upload.add_argument('image', location='files',
#                            type=werkzeug.datastructures.FileStorage, required=True, help="PNG Image")
parser = reqparse.RequestParser()

@api.route('/crimes/timeline/<string:suburb>')
@api.representation('image/png')
class Crime_Timeline(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("Suburb is: ", suburb)
        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )
        # args = file_upload.parse_args()
        # if args['image'].mimetype == 'image/png':
        #     args['image'].save(crime_timeline(suburb))
        # else:
        #     abort(404)

        return crime_timeline(suburb)

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
    # img.seek(0)
    # dictdf = df.to_dict()
    # plot_url = base64.b64encode(img.getvalue())
    output = io.BytesIO()
    # plt.savefig(output, format='png')
    plt.savefig(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response
    # return plot_url

if __name__ == "__main__":
    crime_df = pd.read_csv("crime.csv", dtype={"Incidents Recorded": str})
    app.run(debug=True)