# Housing Prices API

import json
import base64
import io
import werkzeug
import pandas as pd
import numpy as np
from time import time

from flask import Flask
from flask import request, send_file, make_response
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse
from flask_profiler import Profiler
import flask_monitoringdashboard as dashboard

import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn import metrics

from functools import wraps
from itsdangerous import SignatureExpired, JSONWebSignatureSerializer, BadSignature


class AuthenticationToken:
    def __init__(self, secret_key, expires_in):
        self.secret_key = secret_key
        self.expires_in = expires_in
        self.serializer = JSONWebSignatureSerializer(secret_key)

    def generate_token(self, username):
        info = {
            'username': username,
            'creation_time': time()
        }

        token = self.serializer.dumps(info)
        return token.decode()

    def validate_token(self, token):
        info = self.serializer.loads(token.encode())

        if time() - info['creation_time'] > self.expires_in:
            raise SignatureExpired("The Token has been expired; get a new token")

        return info['username']



SECRET_KEY = "A SECRET AND VERY LONG RANDOM STRING USED AS KEY"
expires_in = 600
auth = AuthenticationToken(SECRET_KEY, expires_in)

app = Flask(__name__)
api = Api(app, default="Housing", title="Melbourne Dataset", description="<description here>")


def requires_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')
        
        if (token != 'admintoken'):
            abort(401, "Not admin login")

        return f(*args, **kwargs)
    
    return decorated

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get('AUTH-TOKEN')
        if not token:
            abort(401, 'Authentication token is missing')

        try:
            user = auth.validate_token(token)
        except SignatureExpired as e:
            abort(401, e.message)
        except BadSignature as e:
            abort(401, e.message)

        return f(*args, **kwargs)

    return decorated


credential_model = api.model('credential', {
    'username': fields.String,
    'password': fields.String
})

credential_parser = reqparse.RequestParser()
credential_parser.add_argument('username', type=str)
credential_parser.add_argument('password', type=str)

parser = reqparse.RequestParser()
parser.add_argument('average')
parser.add_argument('start')
parser.add_argument('limit')

dashboard.bind(app)

@api.route('/token')
class Token(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Generates a authentication token")
    @api.expect(credential_parser, validate=True)
    def get(self):
        args = credential_parser.parse_args()

        username = args.get('username')
        password = args.get('password')

        if username == 'admin' and password == 'admin':
            return {"token": "admintoken"}
        elif username == 'user' and password == 'pass':
            return {"token": auth.generate_token(username)}

        return {"message": "authorization has been refused for those credentials."}, 401


@api.route('/realEstateStatistics')
class real_estate(Resource):
    def get(self):
        real_estate = housing_df.groupby('SellerG', as_index=False).size().sort_values(ascending=False)
        return real_estate.to_json()


# Average prices summary of entire Melbourne: returning each suburb and values
@api.route('/suburbs/averagePrice')
class suburb_average_all(Resource):
    def get(self):
        housing_median = housing_df.groupby('Suburb', as_index=False)['Price'].median()
        house_prices = housing_median.round({'Price': -1})
        house_prices = house_prices.rename(columns={"Prices": "Median House Price"})
        # print each to as a line in JSON 
        json = house_prices.to_json(orient='records')
        return json


@api.route('/suburbs/averagePrice/<string:suburb>')
class suburb_average_singular(Resource):
    def get(self,suburb):

        housing_df['Suburb'] = housing_df['Suburb'].str.lower()

        if suburb not in housing_df['Suburb'].values:
            api.abort(404,  'Postcode {} does not exist'.format(suburb) )


        suburb_df = housing_df.loc[housing_df['Suburb'] == suburb]
        housing_median = suburb_df['Price'].median()
       
        return int(housing_median)


@api.route('/crimes')
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
class Crime_PostCode(Resource):
    def get(self, post_code):
        if post_code not in crime_df['Postcode'].values:
            api.abort(404,  'Postcode {} does not exist'.format(post_code) )

        crime_in_post_code = crime_df.loc[crime_df['Postcode'] == post_code]
        suburbs_in_postcode = crime_in_post_code['Suburb/Town Name'].unique()
        total_crimes = crime_in_post_code['Postcode'].count()
        crime_summary = crime_in_post_code.groupby(['Offence Division']).size()
        
        crime_dict = {
            "suburb": suburbs_in_postcode.tolist(),
            "postcode": post_code,
            "total": int(total_crimes),
            "crime_summary": crime_summary.to_json()
        }

        return crime_dict

#singular value for the time being
@api.route('/crimes/<string:suburb>/')
class Crime_Suburb(Resource):
    def get(self, suburb):
        # print("suburb is: ", suburb)
        suburb = suburb.upper()
        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )
        
        crime_in_suburb = crime_df.loc[crime_df['Suburb/Town Name'] == suburb]
        post_code = crime_in_suburb['Postcode'].unique().tolist()[0]
        total_crimes = crime_in_suburb['Suburb/Town Name'].count()
        crime_summary = crime_in_suburb.groupby(['Offence Division']).size()
        
        crime_dict = {
            "suburb": suburb,
            "postcode": int(post_code),
            "total": int(total_crimes),
            "crime_summary": crime_summary.to_json()
        }

        return crime_dict


@api.route('/schools/<string:suburb>')
class School_Suburb(Resource):
    def get(self, suburb):
        suburb = suburb.upper()
        print("suburb is: ", suburb)
        if suburb not in school_df['Postal_Town'].values:
            api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        schools_in_suburb = school_df.loc[school_df['Postal_Town'] == suburb]
        return dict(schools_in_suburb['School_Name'])


@api.route('/schools/ranking/<string:council>')
@api.param('average', 'int specifying whether to show average or individual school ranking')
class Schools_ranking(Resource):
    def get(self, council):
        council = council.upper()
        if council not in list(df['Postal_Town']):
            api.abort(404, 'Council {} does not exist.'.format(council))

        args = parser.parse_args()
        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []
        average = args.get('average')
        print(average)

        avg_ranking = 0
        total = 0
        count = 0
        if not average:
            for item in ds:
                if ds[item]['Postal_Town'] == council:
                    school_ranking = {ds[item]['School_Name'] : ds[item]['School_No']}
                    ret.append(school_ranking)
        else:
            for item in ds:
                if ds[item]['Postal_Town'] == council:
                    total = ds[item]['School_No']
                    count += 1
            avg_ranking = total/count
            ret.append({'Average Ranking' : str(avg_ranking)})
        return ret


@api.route('/schools')
@api.param('start', 'start of page')
@api.param('limit', 'limit of data')
class Schools_pagination(Resource):
    def get(self):
        args = parser.parse_args()
        start = args.get('start')
        limit = args.get('limit')

        if not start:
            start = 0

        if not limit:
            limit = 20

        count = df.shape[0]
        if count < int(start):
            api.abort(404, 'Start value cannot be greater than data size')
        elif int(limit) < 0:
            api.abort(404, 'Limit value cannot be negative')

        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        start_index = 1
        limit_index = 1

        for item in ds:
            if start_index >= int(start):
                ret.append(ds[item])
                limit_index += 1
            if limit_index > int(limit):
                break
            start_index += 1
        return ret


@api.route('/property_pc/<string:post_codes>/')
class Property_PostCode(Resource):

    def get(self, post_codes):
        postcodes_list = post_codes.split(';')
        
        #print(list(map(int,list(df['Postcode']))))

        for post_code in postcodes_list:
            post_code = int(post_code.strip())
            if (post_code not in list(map(int,list(df['Postcode'])))):
                api.abort(404,  'Post Code {} does not exist'.format(post_code) )

        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for item in ds:
            if str(int(ds[item]['Postcode'])) in postcodes_list:
                ret.append(ds[item])


        return ret

@api.route('/property/<string:suburbs>/')
class Property_Suburb(Resource):
    # each suburb is spearated by a delimiter ';'
    def get(self, suburbs):
        suburbs_list = suburbs.split(';')
        for suburb in suburbs_list:
            suburb = suburb.strip()
            if suburb not in list(df['Suburb']):
                api.abort(404,  'Suburb {} does not exist'.format(suburb) )
        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for item in ds:
            if ds[item]['Suburb'] in suburbs_list:
                ret.append(ds[item])


        return ret

    # def put (self, suburbs):


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
        # suburb = suburb.upper()
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


@api.route('/property/sort/<string:sort_by>/<int:asc>')
class Property_Sort(Resource):
     def get(self, sort_by, asc):
        if asc:
            df.sort_values(by=[sort_by], ascending=True, inplace=True)
        else:
            df.sort_values(by=[sort_by], ascending=False, inplace=True)

        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        for item in ds:
            ret.append(ds[item])

        return ret

@api.route('/crimes/timeline/<string:suburb>')
class Crime_Timeline(Resource):
    @api.expect(fields.String)
    def get(self, suburb):
        suburb = suburb.upper()
        print("Suburb is: ", suburb)
        if suburb not in crime_df['Suburb/Town Name'].values:
            api.abort(404, 'Suburb {} does not exist'.format(suburb) )
        return crime_timeline(suburb)

@api.route('/prediction/<distance>', defaults={"prop_type": "h"})
@api.param('prop_type', "A prop type (h, t, u)")
@api.param('distance', "A float between 0 and 35")
class Price_Prediction(Resource):
    def get(self, distance, prop_type):
        try: 
            distance = float(distance)
        except ValueError:
            api.abort(400, "Not a valid input")
        if distance > 35 or distance < 0:
            api.abort(400, 'Distance is outside of CBD prediction')
        if (prop_type == "h" or prop_type == "u" or prop_type == "t"):
            price = str(round(price_prediction(dist=distance, prop_type=prop_type), 2)) 
            price = "$" + price
            return {"Price": price}   
        else:
            api.abort(400, 'Property Type is not valid (h, t, u)')


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
    # do dataset stuff here
    df = pd.read_csv('melb_data.csv')
    df['BuildingArea'] = df['BuildingArea'].fillna(0)
    df['YearBuilt'] = df['YearBuilt'].fillna(0)
    df['Date'] =pd.to_datetime(df.Date)
    #df.astype({'Postcode':'int64'}).dtypes

    housing_df = df
    
    school_df = pd.read_csv('schools.csv', encoding = "ISO-8859-1")
    school_df['Postal_Town'] = school_df['Postal_Town'].str.upper()

    crime_temp = pd.read_csv('crime.csv')
    col_list = ['Suburb/Town Name', 'Postcode', 'Offence Division']
    crime_df = crime_temp[col_list]
    
    melb_df = pd.read_csv("melb_data.csv")
    
    app.run(debug=True)
