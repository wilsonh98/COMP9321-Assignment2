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
            return {"token": auth.generate_token(username)}

        return {"message": "authorization has been refused for those credentials."}, 401



# add @api.routes here
# .
# .
# .

@api.route('/property/<str:suburbs>/')
class Property_Suburb(Resource):
    # each suburb is spearated by a delimiter ';'
    def get(self, suburbs):
        suburbs_list = suburbs.split(';')
        for suburb in suburbs_list:
            if suburb not in df.index:
                api.abort(404,  'Suburb {} does not exist'.format(suburb) )

        prp = dict(df.loc[suburb])
        return prp

    def put (self, suburbs):


@api.route('/property/<int:post_codes>/')
class Property_PostCode(Resource):

    def get(self, post_codes):
        postcodes_list = post_codes.split(';')
        for post_code in post_codes:
            if post_code not in df.index:
                api.abort(404,  'Post Code {} does not exist'.format(post_code) )

        prp = dict(df.loc[post_code])
        return prp


@api.route('/property/<str:suburbs>/<str:price>/<bool:sortBy>/<bool:asc>/')
class Property_Sort_Price(Resource):

     def get(self, suburbs, sortBy, asc):
        if sortBy:
            # do sth
        else:
            # do sth else


@api.route('/property/<int:suburbs>/<data:date>/<bool:sortBy>/<bool:asc>/')
class Property_Sort_Date(Resource):

     def get(self, suburbs, sortBy, asc):
        if sortBy:
            # do sth
        else:
            # do sth else


if __name__ == "__main__":
    # do dataset stuff here
    df = pd.read_csv('melb_data.csv')
    df['BuildingArea'] = df['BuildingArea'].fillna(0)
    df['YearBuilt'] = df['YearBuilt'].fillna(0)
    app.run(debug=True)
