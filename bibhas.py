import pandas as pd
import json
from time import time

from flask import Flask
from flask import request
from flask_restplus import Resource, Api, abort
from flask_restplus import fields
from flask_restplus import inputs
from flask_restplus import reqparse

app = Flask(__name__)
api = Api(app, title = "Schools avg")

parser = reqparse.RequestParser()

@api.route('/schools/ranking/<string:council>')
class Schools_ranking(Resource):

    def get(self, council):
        if council not in list(df['Postal_Town']):
            api.abort(404, 'Council {} does not exist.'.format(council))

        args = parser.parse_args()

        json_str = df.to_json(orient='index')
        ds = json.loads(json_str)
        ret = []

        average = args.get('average')

        for item in ds:
            if ds[item]['Postal_Town'] == council:
                school_ranking = {ds[item]['School_Name'] : ds[item]['School_No']}
                ret.append(school_ranking)

        return ret


if __name__ == '__main__':
    df = pd.read_csv('schools.csv',  encoding = "ISO-8859-1")
    df['Postal_Town'] = df['Postal_Town'].str.upper()

    app.run(debug=True)



