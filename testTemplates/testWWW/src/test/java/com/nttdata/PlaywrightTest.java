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
package com.nttdata;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.Date;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.options.ScreenshotType;
import com.nttdata.model.Calculation;
import com.nttdata.model.ResultData;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Exemplo de utilização do Playwright
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class PlaywrightTest {
    static final String RESULTS_SERVER_URL = "http://localhost:3333/executions";
    static final String PLATFORM = "PLAYWRIGHT JAVA WEB";
    static final String TESTSUITEID = "CALCDATA";

    Playwright playwright;
    Browser browser;
    BrowserContext context;
    Page page;


    @BeforeAll
    public void setup0() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch();
        context = browser.newContext();
        page = context.newPage();
    }


    /**
     * Executa o teste
     * 
     * @throws IOException
     */
    @ParameterizedTest
    @Tag("ply")
    @MethodSource("com.nttdata.model.CalculationStreamGenerator#generator")
    public void testCalculation(Calculation calc) throws IOException {
        ResultData testResult = initResults(calc);

        String obtainedResult = "NO RESULT";
        Double expectedValue = calc.getExpected_value();
        boolean okExecution = true;
        try {
            String p1 = String.valueOf(calc.getFirst_value());
            String op = String.valueOf(calc.getOperator());
            String p2 = String.valueOf(calc.getSecond_value());
            page.navigate("http://localhost:1111");
            page.type("#calcOperation", p1 + " " + op + " " + p2 + "\n");
            obtainedResult = page.innerText("#result");
            assertEquals(expectedValue, Double.parseDouble(obtainedResult), 0.0000999);
            testResult.setPassed(true);
        } catch (AssertionError | Exception e) {
            okExecution = false;
            testResult.setPassed(false);
            testResult.appendComments(e.getMessage());
        } finally {
            try {
                String evidenceFileName = generateScreenshot(okExecution, page);
                testResult.setEvidence(evidenceFileName, "image/png");
            } catch (IOException ioe) {
                okExecution = false;
                testResult.setPassed(false);
                testResult.appendComments("Error storing evidence: " + ioe.getMessage());
            }
            testResult.measureTime();
            testResult.sendResults(RESULTS_SERVER_URL);
        }
        if (!okExecution) {
            fail(testResult.getComments());
        }
    }

    @AfterAll
    public void tearDown() throws IOException {
        context.close();
        playwright.close();
    }

    private ResultData initResults(Calculation calc) {
        ResultData myTestResult = new ResultData();
        myTestResult.setTestId(String.valueOf(calc.getId()));
        myTestResult.setTestSuiteId(TESTSUITEID);
        myTestResult.setPlatform(PLATFORM);
        myTestResult.appendComments("First value : " + calc.getFirst_value());
        myTestResult.appendComments("Second value : " + calc.getSecond_value());
        myTestResult.appendComments("Operator : " + calc.getOperator());
        myTestResult.setBlocked(false);
        myTestResult.setPassed(false);
        return myTestResult;
    }

    /**
     * Método que gera um screenshot da tela
     * 
     * @param driver
     * @throws IOException
     */
    private static synchronized String generateScreenshot(boolean ok, Page pg) throws IOException {
        String isFailed = (ok ? "OK" : "##");
        Date currentTime = new Date();
        SimpleDateFormat format = new SimpleDateFormat("yyyyMMdd-HHmmss-SSS");
        String fileName = "evidence/" + isFailed + "ply-" + format.format(currentTime) + ".png";
        pg.screenshot(new Page.ScreenshotOptions()
                .setPath(Paths.get(fileName))
                .setFullPage(false)
                .setType(ScreenshotType.PNG));
        return fileName;
    }

}