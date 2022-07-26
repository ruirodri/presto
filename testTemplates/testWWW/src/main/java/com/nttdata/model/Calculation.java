/*
Copyright 2022 NTT DATA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
package com.nttdata.model;

public class Calculation {
    private long id;
    private double first_value;
    private double second_value;
    private char operator;
    private double expected_value;

    public Calculation(long id, double first_value, double second_value, char operator, double expected_value) {
        this.id = id;
        this.first_value = first_value;
        this.second_value = second_value;
        this.operator = operator;
        this.expected_value = expected_value;
    }

    public long getId() {
        return id;
    }

    public double getFirst_value() {
        return first_value;
    }

    public double getSecond_value() {
        return second_value;
    }

    public char getOperator() {
        return operator;
    }

    public double getExpected_value() {
        return expected_value;
    }

}
