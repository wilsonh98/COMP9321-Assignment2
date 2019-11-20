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

@api.route('/crime/<int:post_code>/')
class Crime_PostCode(Resource):
    def get(self, post_code):
        if post_code not in crime_df['Postcode'].values:
            api.abort(404,  'Postcode {} does not exist'.format(post_code) )

        crime_in_post_code = crime_df.loc[crime_df['Postcode'] == post_code]
        total_crimes = crime_in_post_code['Postcode'].count()
        crime_summary = crime_in_post_code.groupby(['Offence Division']).size()
        
        crime_dict = {
            "total": int(total_crimes),
            "crime_summary": crime_summary.to_json()
        }

        return crime_dict

#singular value for the time being
@api.route('/crime/<string:suburb>/')
class Crime_Suburb(Resource):
    def get(self, suburb):
        # print("suburb is: ", suburb)
        suburb = suburb.upper()
        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )
        
        crime_in_suburb = crime_df.loc[crime_df['Suburb/Town Name'] == suburb]
        
        total_crimes = crime_in_suburb['Suburb/Town Name'].count()
        crime_summary = crime_in_suburb.groupby(['Offence Division']).size()
        
        crime_dict = {
            "total": int(total_crimes),
            "crime_summary": crime_summary.to_json()
        }

        return crime_dict



@api.route('/schools/<string:suburb>/')
class School_Suburb(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("suburb is: ", suburb)
        if suburb not in df['Postal_Town'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
        return dict(schools_in_suburb['School_Name'])


#cant get schools by post code: it is within different csv
'''@api.route('/schools/<int:post_code>/')
class School_Suburb(Resource):
    def get(self,post_code):
        if post_code not in df['Postcode'].values:
            api.abort(404,  'Suburb {} does not exist'.format(post_code) )

        schools_in_suburb = df.loc[df['Postcode'] == post_code]
        return dict(schools_in_suburb['School_Name']) '''

        
if __name__ == "__main__":
    # do dataset stuff here
    df = pd.read_csv('schools.csv', encoding = "ISO-8859-1")
    df['Postal_Town'] = df['Postal_Town'].str.upper()

    crime_temp = pd.read_excel('crime.xlsx')
    col_list = ['Suburb/Town Name', 'Postcode', 'Offence Division']
    crime_df = crime_temp[col_list]

    app.run(debug=True)
