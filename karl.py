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

# karl import
import matplotlib.pyplot as plt # import matplotlib
import numpy as np

#@api.route(schools/graph/<string:suburb>)

#@api.route(suburbs/graph/<string:suburb>)

# FUNCTIONS TO PLOT

def housing_pie(suburb="Abbotsford"):

    # read in and sanitise
    df = pd.read_csv("melb_data.csv")
    df = df[['Suburb','Type']]
    df = df[df["Suburb"] == suburb]
    
#    print(df.head(5).to_string())
    
    # replace values
    df.loc[df['Type'] == 'h', 'Type'] = 'House'
    df.loc[df['Type'] == 'u', 'Type'] = 'Unit'
    df.loc[df['Type'] == 't', 'Type'] = 'Town House'
    
    # groupby Type
    df = df.groupby(['Type']).count()
    
    # pie chart plot
    df.plot.pie(subplots=True, title = "Accommodation type by Suburb")
    
#    print(df.to_string())

def school_stacked_bar(suburb="CRAIGIEBURN"):

    # read in and sanitise
    df = pd.read_csv("schools.csv", encoding = "ISO-8859-1")
    df = df[['Education_Sector','School_Type', "Postal_Town"]]
    df['Postal_Town'] = df['Postal_Town'].str.upper() # change to upper string
    df = df[df["Postal_Town"] == suburb] # selecting suburb
#    print(df.to_string())
    df.insert(1,'Value',1) # inserting a column of ones for pivot
#    df.reset_index("Education_Sector", inplace = True)
#    print(df.to_string())
    
    # pivot by school_type
    df = df.pivot_table(index='Education_Sector', columns='School_Type', values='Value', aggfunc=np.sum)
    df = df.fillna(0) # fill in null values
    
    # plotting
    df.plot.bar(stacked=True, title = "Education Sector and School Type by Suburb")
    
#    print(df.head(5).to_string())

#    # groupby Type
#    df = df.groupby(['Education_Sector'])
#    print("ceebs")
    
if __name__ == "__main__":
    housing_pie()
    school_stacked_bar()