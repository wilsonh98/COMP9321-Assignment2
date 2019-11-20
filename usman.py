# Housing Prices API

import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

import json
from time import time
from functools import wraps

SECRET_KEY = "A SECRET AND VERY LONG RANDOM STRING USED AS KEY"
expires_in = 600

app = Flask(__name__)
api = Api(app, default="Housing", title="Melbourne Dataset", description="<description here>")



# add @api.routes here
# .
# .
# .

# TO DO: CRIME REPORT ENDPOINT

@api.route('/crime/<string:suburb>/')
class School_Suburb(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("suburb is: ", suburb)
        if suburb not in df['Postal_Town'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
        return dict(schools_in_suburb['School_Name'])



@api.route('/schools/<string:suburb>/')
class School_Suburb(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("suburb is: ", suburb)
        if suburb not in df['Postal_Town'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
        return dict(schools_in_suburb['School_Name'])

            

if __name__ == "__main__":
    # do dataset stuff here
    df = pd.read_csv('schools.csv', encoding = "ISO-8859-1")
    df['Postal_Town'] = df['Postal_Town'].str.upper()

    # crime_df = pd.read_csv('crim.csv', encoding = "ISO-8859-1")

    app.run(debug=True)
