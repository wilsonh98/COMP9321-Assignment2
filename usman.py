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
# resource_fields = api.model('Resource', {
#     'name': fields.String,
# })

school_summary = api.model ('School Summary', {
    "schools": fields.List(fields.String)
})

crime_summary_all = api.model('Overall Crime Report', {
    'total': fields.Integer,
    'crime_summary': fields.String("{\"A Crimes against the person\":72677}")
})

crime_summary = api.model('Crime Report', {
    "suburb": fields.String("ALTONA NORTH"),
    "postcode": fields.Integer,
    'total': fields.Integer,
    'crime_summary': fields.String("{\"A Crimes against the person\":72677}")
})

average_price_list = api.model('Price Summary', {
    "Suburb": fields.String("ALTONA NORTH"),
    "Price": fields.Integer
})




@api.route('/realEstateStatistics')
@api.response(200, 'Success')
@api.response(400, 'Bad Request')
class real_estate(Resource):
    def get(self):
        real_estate = housing_df.groupby('SellerG', as_index=False).size().sort_values(ascending=False)
        return real_estate.to_json()

# Average prices summary of entire Melbourne: returning each suburb and values
@api.route('/suburbs/averagePrice')
@api.response(200, 'Success', [average_price_list]) 
@api.response(404, 'Suburb Not Found')
class suburb_average_all(Resource):
    def get(self):
        housing_median = housing_df.groupby('Suburb', as_index=False)['Price'].median()
        house_prices = housing_median.round({'Price': -1})
        house_prices = house_prices.rename(columns={"Prices": "Median House Price"})
        # print each to as a line in JSON 
        json = house_prices.to_json(orient='records')
        return json

@api.route('/suburbs/averagePrice/<string:suburb>')
@api.response(200, 'Success', average_price_list) 
@api.response(404, 'Suburb Not Found')
class suburb_average_singular(Resource):
    def get(self,suburb):

        housing_df['Suburb'] = housing_df['Suburb'].str.lower()

        if suburb not in housing_df['Suburb'].values:
            api.abort(404,  'Postcode {} does not exist'.format(suburb) )


        suburb_df = housing_df.loc[housing_df['Suburb'] == suburb]
        housing_median = suburb_df['Price'].median()
       
        return int(housing_median)


@api.route('/crimes')
@api.response(200, 'Success', crime_summary_all) 
@api.response(400, 'Bad Request')
class Crime_Suburb_All(Resource):
    def get(self):
        total_crimes = crime_df['Offence Division'].count()
        crime_summary = crime_df.groupby(['Offence Division']).size()
        
        crime_dict = {
            "total": int(total_crimes),
            "crime_summary": crime_summary.to_json()
        }

        return crime_dict

@api.route('/crimes/<int:post_code>/')
@api.response(200, 'Success', crime_summary)
@api.response(400, 'Bad Request')
@api.response(404, 'Post code not found')
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
@api.route('/crimes/<string:suburb>/')
@api.response(200, 'Success',crime_summary) 
@api.response(400, 'Bad Request')
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
@api.response(200, 'Success', school_summary)
@api.response(404, 'Suburb Not Found')
class School_Suburb(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("suburb is: ", suburb)
        if suburb not in school_df['Postal_Town'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        schools_in_suburb = school_df.loc[school_df['Postal_Town'] == suburb]
        schools_list = list(schools_in_suburb['School_Name'].values)

        school_dict = {
            "schoools": schools_list
        }

        return school_dict

        
if __name__ == "__main__":

    #read in housing df
    housing_df = pd.read_csv('melb_data.csv')
    # housing_df['Price'] = housing_df['Price'].to_numeric()

    # do dataset stuff here
    school_df = pd.read_csv('schools.csv', encoding = "ISO-8859-1")
    school_df['Postal_Town'] = school_df['Postal_Town'].str.upper()

    crime_temp = pd.read_csv('crime.csv')
    col_list = ['Suburb/Town Name', 'Postcode', 'Offence Division']
    crime_df = crime_temp[col_list]

    app.run(debug=True)
