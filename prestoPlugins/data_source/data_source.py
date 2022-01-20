#  Copyright 2022 NTT DATA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#         http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from flask import Flask
from flask_restful import Resource, Api, reqparse
import MySQLdb as my
import configparser

app = Flask(__name__)
api = Api(app)

conf_parser = configparser.ConfigParser()
conf_parser.read("data_source_config.txt")

user = conf_parser.get("config", "userDB")
password = conf_parser.get("config", "passwordDB")
host = conf_parser.get("config", "hostDB")
database = conf_parser.get("config", "databaseName")
query = conf_parser.get("config", "query")

db = my.connect(host=host, user=user, passwd=password, db=database)
cursor = db.cursor()
fields_descriptions = {}


def load_field_descriptions():
    for the_field in cursor.description:
        fields_descriptions[the_field[0]] = the_field[1]

def init_db():
    cursor.execute(query)
    load_field_descriptions()

def process_data(linha):
    data_dict = {}
    size = len(cursor.description)
    for index in range(size):
        field_name = cursor.description[index][0]
        field_type = cursor.description[index][1]
        value = linha[index]
        if field_type in [0, 246]:
            value = float(value)
        data_dict[field_name] = value
    return data_dict
        
class Datasource(Resource):
    def get(self):
        data_read = {}
        if cursor.rowcount == -1:
            return {"message": "Please init the database"}, 400
        linha = cursor.fetchone()
        if linha == None:
            # return empty data and 204 No Content
            return {'data': data_read}, 204
        else:
            data_read = process_data(linha)
            return {'data': data_read}, 200  # return data and 200 OK

    def post(self):
        conf_parser = configparser.ConfigParser()
        conf_parser.read("data_source_config.txt")
        reload_key = conf_parser.get("confirmation", "reload_key")

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('reloadKey', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary

        if args['reloadKey'] == reload_key:
            init_db()
            return {
                'message': "Data reset accepted."
            }, 200
        else:
            return {
                'message': "Data reset NOT accepted. Invalid code."
            }, 401


api.add_resource(Datasource, '/datasource')  # add endpoints

if __name__ == '__main__':
    app.run()  # run our Flask app
