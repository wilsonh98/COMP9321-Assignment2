# Housing Prices API

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn import metrics
# from flask import Flask
# from flask import request
# from flask_restplus import Resource, Api, abort
# from flask_restplus import fields
# from flask_restplus import inputs
# from flask_restplus import reqparse

# import json
# from time import time
# from functools import wraps

# SECRET_KEY = "A SECRET AND VERY LONG RANDOM STRING USED AS KEY"
# expires_in = 600

# app = Flask(__name__)
# api = Api(app, default="Housing", title="Melbourne Dataset", description="<description here>")


# @api.route('/schools/<string:suburb>/')
# class School_Suburb(Resource):
#     def get(self, suburb):
#         suburb = suburb.upper()
#         print("suburb is: ", suburb)
#         if suburb not in df['Postal_Town'].values:
#             api.abort(404,  'Suburb {} does not exist'.format(suburb) )

#         schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
#         return dict(schools_in_suburb['School_Name'])

# @api.route('/schools/all/')
# class School_List(Resource):
#     def get(self):


# @api.route('/schools/<string:edu_sec>/')
# class School_Sector(Resource):
#     def get(self, suburb):
#         suburb = suburb.upper()
#         print("suburb is: ", suburb)
#         if suburb not in df['Postal_Town'].values:
#             api.abort(404,  'Suburb {} does not exist'.format(suburb) )

#         schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
#         return dict(schools_in_suburb['School_Name'])

# @api.route('/schools/<string:type>/')
# class School_Type(Resource):
#     def get(self, suburb):
#         suburb = suburb.upper()
#         print("suburb is: ", suburb)
#         if suburb not in df['Postal_Town'].values:
#             api.abort(404,  'Suburb {} does not exist'.format(suburb) )

#         schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
#         return dict(schools_in_suburb['School_Name'])



# @api.route('/schools/<int:id>/')
# class School_ID(Resource):
#     def get(self, suburb):
#         suburb = suburb.upper()
#         print("suburb is: ", suburb)
#         if suburb not in df['Postal_Town'].values:
#             api.abort(404,  'Suburb {} does not exist'.format(suburb) )

#         schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
#         return dict(schools_in_suburb['School_Name'])


# @api.route('/schools/<string:edu_sec>/<int:id>/')
# class School_Sector_ID(Resource):
#     def get(self, suburb):
#         suburb = suburb.upper()
#         print("suburb is: ", suburb)
#         if suburb not in df['Postal_Town'].values:
#             api.abort(404,  'Suburb {} does not exist'.format(suburb) )

#         schools_in_suburb = df.loc[df['Postal_Town'] == suburb]
#         return dict(schools_in_suburb['School_Name'])


# def get_crime_graph(suburb):

# @api.route('/crimes/timeline/<string:suburb>')
# class Crime_Timeline(Resource):
#     def get(self, suburb):
#         get_

# @api.route('/prediction/<float:distance>')
# class Price_Prediction(Resource):
#     def get(self, distance):


def price_prediction(dist=2.5, prop_type="h"):
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
    return y_pred    

def crime_summary(suburb="abbotsford"):
    suburb = suburb.upper()
    df = pd.read_csv('crime.csv', dtype={"Incidents Recorded": str})
    df['Incidents Recorded'] = df['Incidents Recorded'].replace(',','', regex=True)
    df['Incidents Recorded'] = pd.to_numeric(df['Incidents Recorded'])
    df = df[(df['Suburb/Town Name'] == suburb)]
    df = df[['Year ending September', 'Incidents Recorded']]
    df.columns = ['Year', 'Count']
    df = df.groupby(['Year']).sum()
    print(df)

if __name__ == "__main__":
    # do dataset stuff here
    # df = pd.read_csv('schools.csv', encoding = "ISO-8859-1")
    # df['Postal_Town'] = df['Postal_Town'].str.upper()
    # crime_df = pd.read_csv('crime.csv', encoding = "ISO-8859-1")

    # app.run(debug=True)
    # price_prediction()
    crime_summary()
