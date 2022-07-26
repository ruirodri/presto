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

from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
import requests
import json

calculator_url = "http://localhost:2222/calculator"

app = Flask(__name__)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@app.route('/')
def hello():
    parser = reqparse.RequestParser()  # initialize parser
    parser.add_argument("expression", required=False)  # add args
    args = parser.parse_args()  # parse arguments to dictionary

    the_expression = args["expression"]
    fn = ""
    sn = ""
    op = ""
    first = True

    if the_expression:
        for ltr in the_expression:
            if (not ltr.isnumeric() and ltr!="."):
                if ltr != " ":
                    if first:
                        op=ltr
                    else:
                        break
                    first=False
            elif first:
                fn += ltr
            else:
                sn += ltr


        if not is_number(fn) or not is_number(sn) or not op in "+-*/":
            return render_template("index.html", rslt="", msg="Invalid expression: {}".format(the_expression))
        else:
            parameters = {"firstNumber": fn,
                      "secondNumber": sn,
                      "operator": op}
            response_calculation = requests.get(calculator_url, params=parameters)
            result_dict = json.loads(json.dumps(response_calculation.json()))
            obtained_result = float(result_dict["result"])
            return render_template("index.html", rslt=obtained_result, msg=the_expression)    
    else:
        return render_template("index.html", msg=" ") 



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111)  # run our Flask app