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


# @api.route('/token')
# class Token(Resource):
#     @api.response(200, 'Successful')
#     @api.doc(description="Generates a authentication token")
#     # @api.expect(credential_parser, validate=True)
#     def get(self):
#         args = credential_parser.parse_args()

#         username = args.get('username')
#         password = args.get('password')

#         if username == 'admin' and password == 'admin':
#             return {"token": auth.generate_token(username)}

#         return {"message": "authorization has been refused for those credentials."}, 401



# add @api.routes here
# .
# .
# .


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



if __name__ == "__main__":
    # do dataset stuff here
    df = pd.read_csv('melb_data.csv')
    df['BuildingArea'] = df['BuildingArea'].fillna(0)
    df['YearBuilt'] = df['YearBuilt'].fillna(0)
    df['Date'] =pd.to_datetime(df.Date)
    df.astype({'Postcode':'int64'}).dtypes
    app.run(debug=True)
