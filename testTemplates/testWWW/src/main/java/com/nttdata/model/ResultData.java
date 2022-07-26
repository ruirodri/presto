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
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.json.JSONObject;

public class ResultData {
    private String testId;
    private String testSuiteId;
    private String platform;
    private Date executionStartDate;
    private float executionDurationSeconds;
    private boolean passed;
    private boolean blocked;
    private String comments;
    private String base64EncodedEvidence;
    private String evidenceFileName;
    private String evidenceMimeType;

    public ResultData(String testId, String testSuiteId, String platform, long executionDurationSeconds, boolean passed,
            boolean blocked, String comments, byte[] evidence,
            String evidenceFileName, String evidenceMimeType) throws IOException {
        this.testId = testId;
        this.testSuiteId = testSuiteId;
        this.platform = platform;
        this.executionDurationSeconds = executionDurationSeconds;
        this.passed = passed;
        this.blocked = blocked;
        this.comments = comments;
        this.evidenceFileName = evidenceFileName;
        this.base64EncodedEvidence = encodeFileToBase64Binary(evidenceFileName);
        this.evidenceMimeType = evidenceMimeType;
        this.executionStartDate = new Date();
    }

    public ResultData() {
        this.executionStartDate = new Date();
        this.comments = "";
    }

    public String getTestId() {
        return testId;
    }

    public void setTestId(String testId) {
        this.testId = testId;
    }

    public String getTestSuiteId() {
        return testSuiteId;
    }

    public void setTestSuiteId(String testSuiteId) {
        this.testSuiteId = testSuiteId;
    }

    public String getPlatform() {
        return platform;
    }

    public void setPlatform(String platform) {
        this.platform = platform;
    }

    public Date getExecutionStartDate() {
        return executionStartDate;
    }

    public float getExecutionDurationSeconds() {
        return executionDurationSeconds;
    }

    public boolean isPassed() {
        return passed;
    }

    public void setPassed(boolean passed) {
        this.passed = passed;
    }

    public boolean isBlocked() {
        return blocked;
    }

    public void setBlocked(boolean blocked) {
        this.blocked = blocked;
    }

    public String getComments() {
        return comments;
    }

    public void setComments(String comments) {
        this.comments = comments;
    }

    public String getBase64EncodedEvidence() {
        return base64EncodedEvidence;
    }

    public String getEvidenceFileName() {
        return evidenceFileName;
    }

    public void setEvidence(String fileName, String mimeType) throws IOException {
        setEvidenceMimeType(mimeType);
        setEvidenceFileName(fileName);
    }

    private void setEvidenceFileName(String evidenceFileName) throws IOException {
        this.evidenceFileName = evidenceFileName;
        int MAX_READ_TRIES = 3;
        int currentTry = 0;
        while (currentTry < MAX_READ_TRIES) {
            try {
                base64EncodedEvidence = encodeFileToBase64Binary(evidenceFileName);
                break;
            } catch (IOException ioe) {
                currentTry += 1; 
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public String getEvidenceMimeType() {
        return evidenceMimeType;
    }

    private void setEvidenceMimeType(String evidenceMimeType) {
        this.evidenceMimeType = evidenceMimeType;
    }

    private static String encodeFileToBase64Binary(String fileName) throws IOException {
        File file = new File(fileName);
        byte[] encoded = Base64.encodeBase64(FileUtils.readFileToByteArray(file));
        return new String(encoded, StandardCharsets.UTF_8);
    }

    public void measureTime() {
        this.executionDurationSeconds = (new Date().getTime() - this.getExecutionStartDate().getTime()) / 1000.0f;
    }

    public void appendComments(String oneMoreComment) {
        StringBuffer cmnts = new StringBuffer(this.comments);
        cmnts.append(" | ");
        cmnts.append(oneMoreComment);
        this.comments = cmnts.toString();
    }

    /**
     * Método que envia os resultados para o servico REST
     * 
     * @param ok
     * @throws IOException
     */
    public String sendResults(String serverAdress) throws MalformedURLException, IOException {
        StringBuffer theJson;
        URL url;
        HttpURLConnection conn;
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        JSONObject jsn;
        final int MAXTRIES = 5;
        int tries = 0;

        while (tries < MAXTRIES) {
            theJson = new StringBuffer();
            url = new URL(serverAdress);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json; utf-8");
            conn.setRequestProperty("Accept", "application/json");
            conn.setDoOutput(true);

            String theDate = sdf.format(this.getExecutionStartDate());

            jsn = new JSONObject();
            jsn.put("test_id", this.getTestId());
            jsn.put("test_suite_id", this.getTestSuiteId());
            jsn.put("platform", this.getPlatform());
            jsn.put("execution_start_date", theDate);
            jsn.put("execution_duration_seconds", String.valueOf(this.getExecutionDurationSeconds()));
            jsn.put("passed", (this.isPassed() ? "true" : "false"));
            jsn.put("blocked", (this.isBlocked() ? "true" : "false"));
            jsn.put("comments", this.getComments());
            jsn.put("evidence", this.getBase64EncodedEvidence());
            jsn.put("evidence_file_name", this.getEvidenceFileName());
            jsn.put("evidence_mime_type", this.getEvidenceMimeType());

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsn.toString().getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            if (conn.getResponseCode() == 200) {
                BufferedReader br = new BufferedReader(new InputStreamReader(
                        (conn.getInputStream())));
                String output;
                while ((output = br.readLine()) != null)
                    theJson.append(output);
                conn.disconnect();
                return theJson.toString();
            } else {
                conn.disconnect();
                tries += 1;
            }
        }
        throw new IOException("Failed to send the results to server.");
    }

}
