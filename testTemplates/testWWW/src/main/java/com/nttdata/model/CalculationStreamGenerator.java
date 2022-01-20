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

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.stream.Stream;

import org.json.JSONObject;

public class CalculationStreamGenerator {

    private static final String DATA_SERVER_URL = "http://localhost:5000/datasource";

    public static Stream<Calculation> generator() {
        return Stream.generate(CalculationStreamGenerator::getCalculation).takeWhile(clc -> (clc != null));
    }

    private static synchronized String readData() throws MalformedURLException, IOException {
        StringBuffer theJson = new StringBuffer();
        URL url = new URL(DATA_SERVER_URL);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        if (conn.getResponseCode() != 200) {
            if (conn.getResponseCode() == 204) // when there is no more data we get a 204 code
                return null;
            else
                throw new RuntimeException("Failed : HTTP error code : "
                        + conn.getResponseCode());
        }
        BufferedReader br = new BufferedReader(new InputStreamReader(
                (conn.getInputStream())));
        String output;
        while ((output = br.readLine()) != null)
            theJson.append(output);
        conn.disconnect();
        return theJson.toString();
    }

    private static synchronized Calculation getCalculation() {
        String dataRead = null;
        try {
            dataRead = readData();
            if (dataRead == null) {
                return null;
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        JSONObject jo = new JSONObject(dataRead).getJSONObject("data");
        return new Calculation(jo.getLong("id"),
                jo.getDouble("first_number"),
                jo.getDouble("second_number"),
                jo.getString("operator").charAt(0),
                jo.getDouble("expected_result"));
    }
}
