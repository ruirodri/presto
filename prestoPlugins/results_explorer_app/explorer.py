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
import MySQLdb as my
import configparser
from datetime import datetime, timedelta
import base64
import math

app = Flask(__name__)

conf_parser = configparser.ConfigParser()
conf_parser.read("data_source_config.txt")

user = conf_parser.get("config", "userDB")
password = conf_parser.get("config", "passwordDB")
host = conf_parser.get("config", "hostDB")
database = conf_parser.get("config", "databaseName")

query = """
select 
    id, 
    test_id, 
    test_suite_id, 
    platform, 
    execution_start_date, 
    execution_duration_seconds, 
    passed, 
    blocked, 
    comments
from 
    test_executions
"""



@app.route('/')
def hello():
    db = my.connect(host=host, user=user, passwd=password, db=database)
    cursor = db.cursor()

    parser = reqparse.RequestParser()  # initialize parser
    parser.add_argument("filterStartingTime", location='args', required=False)  # add args
    parser.add_argument("filterEndingTime", location='args', required=False)
    parser.add_argument("passedfailed", location='args', required=False)
    parser.add_argument("browser", location='args', required=False)
    parser.add_argument("pageNumber", location='args', required=False)
    args = parser.parse_args()  # parse arguments to dictionary

    starting_time = args["filterStartingTime"]
    ending_time = args["filterEndingTime"]
    passed_failed = args["passedfailed"]
    page_number = args["pageNumber"]

    date_format = "%Y-%m-%dT%H:%M"
    if starting_time and ending_time:
        start = datetime.strptime(starting_time, date_format)
        end = datetime.strptime(ending_time, date_format)
    else:
        end = datetime.now()
        start = end - timedelta(hours=1)
        starting_time = datetime.strftime(start, date_format)
        ending_time = datetime.strftime(end, date_format)

    where_clause = " WHERE execution_start_date >= \"{}\" and execution_start_date <= \"{}\"".format(
            start, end)

    selpass = ""
    selfail = ""
    selboth = ""
    if passed_failed and passed_failed != "both":
        if passed_failed == "passed":
            where_clause += " AND PASSED={}".format(1)
            selpass = "selected"
        else:
            where_clause += " AND PASSED={}".format(0)
            selfail = "selected"
    else:
        selboth = "selected"
    
    qryCount = "select count(id) from test_executions"+where_clause
    cursor.execute(qryCount)
    lineCount = cursor.fetchone()
    qt_records = lineCount[0]
    
    PER_PAGE = 500
    pages = math.ceil(qt_records / PER_PAGE)
    if pages == 0:
        pages = 1

    if page_number:
        int_page_number = int(page_number)
        if int_page_number > pages:
            int_page_number = pages
    else:
        int_page_number = 1

    starting_record = (int_page_number -1)*PER_PAGE
    ending_record=starting_record+PER_PAGE
    if ending_record > qt_records:
        ending_record = qt_records

    where_clause += " limit {}, {}".format(starting_record, PER_PAGE)

    list_pages = []
    for x in range(1, pages+1):
        list_pages.append(x)

    query2 = query+where_clause
    cursor.execute(query2)
    
    linhas_dados = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("index.html",
                           startingTime=starting_time,
                           endingTime=ending_time,
                           qtRecords=qt_records,
                           linhas=linhas_dados,
                           spass=selpass,
                           sfail=selfail,
                           sboth=selboth,
                           listPages=list_pages,
                           startingRecord=starting_record,
                           endingRecord=ending_record,
                           pageNumber=int_page_number 
                           )


@app.route('/exec')
def one():
    db = my.connect(host=host, user=user, passwd=password, db=database)
    cursor = db.cursor()

    query_one = """
    select 
        id, 
        test_id, 
        test_suite_id, 
        platform, 
        execution_start_date, 
        execution_duration_seconds, 
        passed, 
        blocked, 
        comments,
        evidence,
        evidence_mime_type
    from 
        test_executions
    """

    parser = reqparse.RequestParser()  # initialize parser
    parser.add_argument("execId", location='args', required=True)  # add args
    args = parser.parse_args()  # parse arguments to dictionary
    query2 = query_one + " WHERE id={}".format(args["execId"])
    cursor.execute(query2)
    line = cursor.fetchone()
    byte_evidence = line[9]
    evidence=""
    if byte_evidence != None:
        evidence = byte_evidence.decode("utf-8")
    mime_type = line[10]
    if not mime_type:
        mime_type = "text/plain"

    cursor.close()
    db.close()

    return render_template("oneExec.html", linha=line, evid=evidence, mimeType=mime_type)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777)  # run our Flask app
