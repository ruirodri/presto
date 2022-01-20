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
conf_parser.read("database_config.txt")

user = conf_parser.get("config", "userDB")
password = conf_parser.get("config", "passwordDB")
host = conf_parser.get("config", "hostDB")
database = conf_parser.get("config", "databaseName")
table_name = conf_parser.get("config", "tableName")

db = my.connect(host=host, user=user, passwd=password, db=database)
cursor = db.cursor()


#  def init_db():
#      cursor.execute(query)
#      load_field_descriptions()


db_creation_statement = "create database if not exists {}; use {};".format(
    database, database)

table_creation_statement = """
create table if not exists {} (
    id int auto_increment primary key,
    test_id varchar(20) not null,
    test_suite_id varchar(20),
    platform varchar(50),
    execution_start_date datetime not null,
    execution_duration_seconds decimal(12,4) not null,
    passed boolean not null,
    blocked boolean not null,
    comments varchar(255),
    evidence blob,
    evidence_file_name varchar(255),
    evidence_mime_type varchar(20)
 );
""".format(table_name)

cursor.execute(db_creation_statement)
cursor.execute(table_creation_statement)
cursor.close()
db.close()



class Store_executions(Resource):
    def get(self):
        data_example = {"test_id": "01234567890123456789",
                        "test_suite_id": "01234567890123456789",
                        "platform": "Browser Edge",
                        "execution_start_date": "2012-04-23T18:25:43.511Z",
                        "execution_duration_seconds": 99.9999,
                        "passed": True,
                        "blocked": False,
                        "comments": "first number was 23.5 and second number was 22.5; operator was /",
                        "evidence": "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAAzSURBVChTY/iPFyCk38qoQBCUDwZQaWRRZDZIGk0HEMBFiJAGAmQVyGzinIYLUCL9/z8Abj4RhPJ2/tYAAAAASUVORK5CYII=",
                        "evidence_file_name": "bolinha.png",
                        "evidence_mime_type": "image/png"
                        }
        return data_example, 200  # return payload example and 200 OK

    def post(self):
        db = my.connect(host=host, user=user, passwd=password, db=database)
        cursor = db.cursor()

        parser = reqparse.RequestParser()  # initialize parser
        parser.add_argument("test_id", required=True)  # add args
        parser.add_argument("test_suite_id", required=False)
        parser.add_argument("platform", required=False)
        parser.add_argument("execution_start_date", required=True)
        parser.add_argument("execution_duration_seconds", required=True)
        parser.add_argument("passed", required=True)
        parser.add_argument("blocked", required=True)
        parser.add_argument("comments", required=False)
        parser.add_argument("evidence", required=False)
        parser.add_argument("evidence_file_name", required=False)
        parser.add_argument("evidence_mime_type", required=False)
        args = parser.parse_args()  # parse arguments to dictionary

        mime_type = args["evidence_mime_type"]
        if mime_type:
            if not mime_type in ["text/plain", "image/png", "image/jpeg"]:
                return {"message": "Invalid evidence mime type. The currently supported formats are text/plain, image/png and image/jpeg."}, 400
        else:
            mime_type = "text/plain"

        values = (args["test_id"],
                  args["test_suite_id"],
                  args["platform"],
                  args["execution_start_date"],
                  args["execution_duration_seconds"],
                  int(True if args["passed"] == "true" else False),
                  int(True if args["blocked"] == "true" else False),
                  args["comments"][:255],
                  args["evidence"],
                  args["evidence_file_name"],
                  args["evidence_mime_type"])

        insert_statement = "insert into {} ".format(table_name)
        insert_statement = insert_statement + \
            "values (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_statement, values)

        db.commit()
        cursor.close()
        db.close()
        return {"message": "data inserted with ID {}".format(cursor.lastrowid)}, 200


api.add_resource(Store_executions, "/executions")  # add endpoints

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333)  # run our Flask app
