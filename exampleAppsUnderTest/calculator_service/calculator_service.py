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
# import MySQLdb as my
import configparser
import time
import random

app = Flask(__name__)
api = Api(app)


class Calculator(Resource):
    def get(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('firstNumber', location='args', required=True)  # add args
        parser.add_argument('secondNumber', location='args', required=True)  # add args
        parser.add_argument('operator', location='args', required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary

        first_number = float(args["firstNumber"])
        second_number = float(args["secondNumber"])
        operator = str(args["operator"])
        result = 0.0

        if operator == "+":
            result = first_number + second_number
        elif operator == "-":
            result = first_number - second_number
        elif operator == "*":
            result = first_number * second_number
        elif operator == "/":
            result = first_number / second_number
        else:
            return {"message":"Invalid Operator."}, 400

        result = round(result,4)
        
        dict_result = {"firstNumber": first_number,
                       "secondNumber": second_number, "operator": operator, "result": result}
        #  time.sleep(random.uniform(0, 0.5))
        return dict_result, 200


api.add_resource(Calculator, '/calculator')  # add endpoints

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2222)  # run our Flask app
