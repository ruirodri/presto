import requests
import json
import time
import math
import itertools


calculator_url = "http://localhost:2222/calculator"
datasource_url = "http://localhost:5000/datasource"
store_executions_url = "http://localhost:3333/executions"

passed = 0
failed = 0

start_time = time.time()

test_suite_id = "CALCIA"
platform = "SERVICE CALCULATOR"

response_data = requests.get(datasource_url)



# Define os vetores com os operadores lógicos e caracteres especiais e o vetor com valores de 0 a 9
operator = ['*', '/', '-', '+','@', '#', '$', '%', '*', '!']
valores = range(10)
aux = 0

while response_data.status_code == 200:
    start_test_time = time.time()
    test_suite_id = operator[0]

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

