import pandas as pd
import json
from time import time

from flask import Flask
from flask import request, jsonify
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

app = Flask(__name__)
api = Api(app, title = "Schools avg")

parser = reqparse.RequestParser()
parser.add_argument('average')
parser.add_argument('start')
parser.add_argument('limit')

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



if __name__ == '__main__':
    df = pd.read_csv('schools.csv',  encoding = "ISO-8859-1")
    df['Postal_Town'] = df['Postal_Town'].str.upper()

    app.run(debug=True)



