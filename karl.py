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

@api.route('/schools/graph/<string:suburb>')
class School_stacked_bar(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("Suburb is: ", suburb)
        if suburb not in school_df['Postal_Town'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )
        return school_stacked_bar(suburb)

@api.route('/suburbs/graph/<string:suburb>')
class Housing_pie(Resource):
    def get(self, suburb):
#        suburb = suburb.upper()
        print("Suburb is: ", suburb)
        if suburb not in melb_df['Suburb'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )
        return housing_pie(suburb)


# FUNCTIONS TO PLOT

def housing_pie(suburb="Abbotsford"):

    # read in and sanitise
    df = pd.read_csv("melb_data.csv")
    df = df[['Suburb','Type']]
    df = df[df["Suburb"] == suburb]
    
    # replace values
    df.loc[df['Type'] == 'h', 'Type'] = 'House'
    df.loc[df['Type'] == 'u', 'Type'] = 'Unit'
    df.loc[df['Type'] == 't', 'Type'] = 'Town House'
    
    # groupby Type
    df = df.groupby(['Type']).count()
    
    # pie chart plot
    df.plot.pie(subplots=True, title = "Accommodation type by Suburb")
    
    output = io.BytesIO()
    plt.savefig(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

def school_stacked_bar(suburb="CRAIGIEBURN"):

    # read in and sanitise
    df = pd.read_csv("schools.csv", encoding = "ISO-8859-1")
    df = df[['Education_Sector','School_Type', "Postal_Town"]]
    df['Postal_Town'] = df['Postal_Town'].str.upper() # change to upper string
    df = df[df["Postal_Town"] == suburb] # selecting suburb
    df.insert(1,'Value',1) # inserting a column of ones for pivot
    
    # pivot by school_type
    df = df.pivot_table(index='Education_Sector', columns='School_Type', values='Value', aggfunc=np.sum)
    df = df.fillna(0) # fill in null values
    
    # plotting
    df.plot.bar(stacked=True, title = "Education Sector and School Type by Suburb")
    
    output = io.BytesIO()
    plt.savefig(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response
    
if __name__ == "__main__":
#    housing_pie()
#    school_stacked_bar()
    school_df = pd.read_csv("schools.csv", encoding = "ISO-8859-1")
    melb_df = pd.read_csv("melb_data.csv")
    app.run(debug=True)
