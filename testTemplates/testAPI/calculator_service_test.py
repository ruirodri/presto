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

# Endpoints for the services in use
calculator_url = "http://localhost:2222/calculator"
datasource_url = "http://localhost:5000/datasource"
store_executions_url = "http://localhost:3333/executions"

# IDs for the test
test_suite_id = "CALCDATA"
platform = "SERVICE CALCULATOR"

# we will count passed and failed tests
passed = 0
failed = 0

# the time when the tests are starting
start_time = time.time()

# get the first set of input data
response_data = requests.get(datasource_url)

# when the data is over, the data source will return us a 204
while response_data.status_code == 200:
    # the time when this test starts
    start_test_time = time.time()

    # parsing the input data json
    stringdata = response_data.text
    input_data = json.loads(stringdata)
    input_data = json.loads(json.dumps(input_data["data"]))

    id = input_data["id"]
    first_number = float(input_data["first_number"])
    second_number = float(input_data["second_number"])
    operator = str(input_data["operator"][0])
    expected_result = float(input_data["expected_result"])

    # preparing the parameters to call the API under test
    parameters = {"firstNumber": first_number,
                  "secondNumber": second_number,
                  "operator": operator}
    
    # calling the API
    response_calculation = requests.get(calculator_url, params=parameters)
    result_dict = json.loads(json.dumps(response_calculation.json()))
    obtained_result = float(result_dict["result"])
    
    # evaluating the result
    ok = False
    if math.fabs(expected_result - obtained_result) < 0.0000999:
        passed += 1
        ok = True
    else:
        failed += 1

    # preparing the result to be stored
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

    # storing the test result on pRESTo!'s endpoint (ten retries at max)
    response_store_execution = requests.post(
        store_executions_url, params=execution_data)
    retries = 0
    while response_store_execution.status_code != 200 and retries < 10:
        response_store_execution = requests.post(
            store_executions_url, params=execution_data)
        retries += 1 

    # obtaining the next set of input data, for the next loop.
    response_data = requests.get(datasource_url)
    
    # showing the execution status at every 100 tests
    if ((passed + failed) % 100) == 0:
        print(" ==> Executed %03.0d tests." % ((passed+failed)))


# this is shown at the end of the execution
print("\n\n============================================")
print(" Executed %03.0d tests in %05.2f seconds " %
      ((passed+failed), (time.time() - start_time)))
print(" Passed %03.0d, failed %03.0d" % (passed, failed))
print("============================================")