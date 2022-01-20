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

import requests
import json
import time
import math

calculator_url = "http://localhost:2222/calculator"
datasource_url = "http://localhost:5000/datasource"
store_executions_url = "http://localhost:3333/executions"

test_suite_id = "CALCDATA"
platform = "SERVICE CALCULATOR"

passed = 0
failed = 0

start_time = time.time()

response_data = requests.get(datasource_url)

while response_data.status_code == 200:
    start_test_time = time.time()

    stringdata = response_data.text
    input_data = json.loads(stringdata)
    input_data = json.loads(json.dumps(input_data["data"]))

    id = input_data["id"]
    first_number = float(input_data["first_number"])
    second_number = float(input_data["second_number"])
    operator = str(input_data["operator"][0])
    expected_result = float(input_data["expected_result"])

    parameters = {"firstNumber": first_number,
                  "secondNumber": second_number,
                  "operator": operator}
    response_calculation = requests.get(calculator_url, params=parameters)
    result_dict = json.loads(json.dumps(response_calculation.json()))
    obtained_result = float(result_dict["result"])
    ok = False
    if math.fabs(expected_result - obtained_result) < 0.0000999:
        passed += 1
        ok = True
    else:
        failed += 1

    comments = "First number {}, second {},  operator {}. The expected result is {}".format(
        first_number, second_number, operator, expected_result)
    str_date = time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(start_test_time))
    execution_data = {"test_id": str(id),
                      "test_suite_id": test_suite_id,
                      "platform": platform,
                      "execution_start_date": str_date,
                      "execution_duration_seconds": (time.time()-start_test_time, ),
                      "passed": ("true" if ok else "false"),
                      "blocked": "false",
                      "comments": comments,
                      "evidence": json.dumps(response_calculation.json()),
                      "evidence_mime_type": "text/plain"}
    response_store_execution = requests.post(
        store_executions_url, params=execution_data)
    while response_store_execution.status_code != 200:
        response_store_execution = requests.post(
        store_executions_url, params=execution_data)

    response_data = requests.get(datasource_url)
    if ((passed + failed) % 100) == 0:
        print(" ==> Executados %03.0d testes até agora." % ((passed+failed)))        

print("\n\n============================================")
print(" Executados %03.0d testes em %05.2f segundos " %
      ((passed+failed), (time.time() - start_time)))
print(" Passados %03.0d, falhados %03.0d" % (passed, failed))
print("============================================")
