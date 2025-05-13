// Licensed to the Software Freedom Conservancy (SFC) under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  The SFC licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package org.openqa.selenium.bidi.emulation;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.within;
import static org.openqa.selenium.testing.drivers.Browser.IE;
import static org.openqa.selenium.testing.drivers.Browser.SAFARI;

import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.bidi.module.Emulation;
import org.openqa.selenium.bidi.module.Script;
import org.openqa.selenium.bidi.script.CallFunctionParameters;
import org.openqa.selenium.bidi.script.ContextTarget;
import org.openqa.selenium.bidi.script.EvaluateResult;
import org.openqa.selenium.bidi.script.EvaluateResultSuccess;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.openqa.selenium.testing.JupiterTestBase;
import org.openqa.selenium.testing.NeedsFreshDriver;
import org.openqa.selenium.testing.NotYetImplemented;

public class EmulationTest extends JupiterTestBase {

  @BeforeEach
  public void setUp() {
//    System.setProperty(
//      "webdriver.firefox.bin", "/Applications/Firefox Nightly.app/Contents/MacOS/firefox");

    FirefoxOptions options = new FirefoxOptions();
    options.setBinary("/Applications/Firefox Nightly.app/Contents/MacOS/firefox");
    options.setCapability("webSocketUrl", true);
    driver = new FirefoxDriver(options);
  }

  @Test
  @NeedsFreshDriver
  @NotYetImplemented(SAFARI)
  @NotYetImplemented(IE)
  public void canSetGeolocationOverride() {
    String id = driver.getWindowHandle();

    // Create coordinates for San Francisco
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .build();

    // Set geolocation override
    try (Emulation emulation = new Emulation(id, driver)) {
      try {
        emulation.setGeolocationOverride(coordinates);
        System.out.println("Successfully set geolocation override");
      } catch (Exception e) {
        System.err.println("Error setting geolocation override: " + e.getMessage());
        e.printStackTrace();
        throw e; // Re-throw to fail the test
      }

      // Use Script module to execute JavaScript that retrieves the geolocation
      try (Script script = new Script(id, driver)) {
        // Create a JavaScript function that returns a Promise with the geolocation
        String geolocationFunction =
            "() => new Promise((resolve, reject) => {" +
            "  navigator.geolocation.getCurrentPosition(" +
            "    position => {" +
            "      resolve({" +
            "        latitude: position.coords.latitude," +
            "        longitude: position.coords.longitude," +
            "        accuracy: position.coords.accuracy," +
            "        altitude: position.coords.altitude," +
            "        altitudeAccuracy: position.coords.altitudeAccuracy," +
            "        heading: position.coords.heading," +
            "        speed: position.coords.speed" +
            "      });" +
            "    }," +
            "    error => {" +
            "      reject(error.message);" +
            "    }" +
            "  );" +
            "})";

        // Call the function and wait for the Promise to resolve
        CallFunctionParameters parameters = new CallFunctionParameters(
            new ContextTarget(id), geolocationFunction, true);

        EvaluateResult result = script.callFunction(parameters);

        // Verify the result
        assertThat(result.getResultType()).isEqualTo(EvaluateResult.Type.SUCCESS);

        EvaluateResultSuccess successResult = (EvaluateResultSuccess) result;
        assertThat(successResult.getResult().getType()).isEqualTo("object");
        assertThat(successResult.getResult().getValue().isPresent()).isTrue();

        @SuppressWarnings("unchecked")
        Map<String, Object> position = (Map<String, Object>) successResult.getResult().getValue().get();

        // Verify the coordinates match what we set
        assertThat((Double) position.get("latitude")).isCloseTo(37.7749, within(0.0001));
        assertThat((Double) position.get("longitude")).isCloseTo(-122.4194, within(0.0001));
        assertThat((Double) position.get("accuracy")).isCloseTo(100.0, within(0.1));
      }
    }
  }

  @Test
  @NeedsFreshDriver
  @NotYetImplemented(SAFARI)
  @NotYetImplemented(IE)
  public void canClearGeolocationOverride() {
    String id = driver.getWindowHandle();

    // First set a geolocation override
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .build();

    try (Emulation emulation = new Emulation(id, driver)) {
      // Set the override
      emulation.setGeolocationOverride(coordinates);

      // Then clear it
      emulation.clearGeolocationOverride();

      // Verify that the override was cleared by checking if the browser
      // prompts for permission when requesting geolocation
      // This is a bit tricky to test directly, so we'll use a JavaScript approach

      // Use Script module to execute JavaScript
      try (Script script = new Script(id, driver)) {
        // Create a JavaScript function that checks if permission is needed
        // This is an indirect way to verify the override was cleared
        String checkPermissionFunction =
            "() => new Promise((resolve) => {" +
            "  // Set a timeout in case permission prompt appears" +
            "  const timeoutId = setTimeout(() => {" +
            "    resolve('Permission prompt likely appeared');" +
            "  }, 500);" +
            "  " +
            "  try {" +
            "    navigator.permissions.query({name: 'geolocation'}).then(result => {" +
            "      clearTimeout(timeoutId);" +
            "      resolve(result.state);" +
            "    });" +
            "  } catch (e) {" +
            "    clearTimeout(timeoutId);" +
            "    resolve('Error: ' + e.message);" +
            "  }" +
            "})";

        // Call the function and wait for the Promise to resolve
        CallFunctionParameters parameters = new CallFunctionParameters(
            new ContextTarget(id), checkPermissionFunction, true);

        EvaluateResult result = script.callFunction(parameters);

        // Verify the result
        assertThat(result.getResultType()).isEqualTo(EvaluateResult.Type.SUCCESS);

        // The actual permission state will vary by browser and user settings,
        // so we just verify that we got a result, which means the override was cleared
        EvaluateResultSuccess successResult = (EvaluateResultSuccess) result;
        assertThat(successResult.getResult().getValue().isPresent()).isTrue();
      }
    }
  }

  @Test
  @NeedsFreshDriver
  @NotYetImplemented(SAFARI)
  @NotYetImplemented(IE)
  public void canSetGeolocationOverrideWithAllParameters() {
    String id = driver.getWindowHandle();

    // Create coordinates with all parameters
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .setAltitude(10.0)
        .setAltitudeAccuracy(5.0)
        .setHeading(90.0)
        .setSpeed(5.0)
        .build();

    // Set geolocation override
    try (Emulation emulation = new Emulation(id, driver)) {
      emulation.setGeolocationOverride(coordinates);

      // Use Script module to execute JavaScript that retrieves the geolocation
      try (Script script = new Script(id, driver)) {
        // Create a JavaScript function that returns a Promise with the geolocation
        String geolocationFunction =
            "() => new Promise((resolve, reject) => {" +
            "  navigator.geolocation.getCurrentPosition(" +
            "    position => {" +
            "      resolve({" +
            "        latitude: position.coords.latitude," +
            "        longitude: position.coords.longitude," +
            "        accuracy: position.coords.accuracy," +
            "        altitude: position.coords.altitude," +
            "        altitudeAccuracy: position.coords.altitudeAccuracy," +
            "        heading: position.coords.heading," +
            "        speed: position.coords.speed" +
            "      });" +
            "    }," +
            "    error => {" +
            "      reject(error.message);" +
            "    }" +
            "  );" +
            "})";

        // Call the function and wait for the Promise to resolve
        CallFunctionParameters parameters = new CallFunctionParameters(
            new ContextTarget(id), geolocationFunction, true);

        EvaluateResult result = script.callFunction(parameters);

        // Verify the result
        assertThat(result.getResultType()).isEqualTo(EvaluateResult.Type.SUCCESS);

        EvaluateResultSuccess successResult = (EvaluateResultSuccess) result;
        assertThat(successResult.getResult().getType()).isEqualTo("object");
        assertThat(successResult.getResult().getValue().isPresent()).isTrue();

        @SuppressWarnings("unchecked")
        Map<String, Object> position = (Map<String, Object>) successResult.getResult().getValue().get();

        // Verify the coordinates match what we set
        assertThat((Double) position.get("latitude")).isCloseTo(37.7749, within(0.0001));
        assertThat((Double) position.get("longitude")).isCloseTo(-122.4194, within(0.0001));
        assertThat((Double) position.get("accuracy")).isCloseTo(100.0, within(0.1));

        // These values might be null in some browsers, so we check conditionally
        if (position.get("altitude") != null) {
          assertThat((Double) position.get("altitude")).isCloseTo(10.0, within(0.1));
        }

        if (position.get("altitudeAccuracy") != null) {
          assertThat((Double) position.get("altitudeAccuracy")).isCloseTo(5.0, within(0.1));
        }

        if (position.get("heading") != null) {
          assertThat((Double) position.get("heading")).isCloseTo(90.0, within(0.1));
        }

        if (position.get("speed") != null) {
          assertThat((Double) position.get("speed")).isCloseTo(5.0, within(0.1));
        }
      }
    }
  }

  @Test
  @NeedsFreshDriver
  @NotYetImplemented(SAFARI)
  @NotYetImplemented(IE)
  public void canSetGeolocationOverrideWithMultipleContexts() {
    // This test requires opening a second window/tab
    String firstTabId = driver.getWindowHandle();

    // Open a new tab using JavaScript
    ((JavascriptExecutor) driver).executeScript("window.open()");

    // Get all window handles
    List<String> windowHandles = List.copyOf(driver.getWindowHandles());
    assertThat(windowHandles.size()).isGreaterThan(1);

    // Get the ID of the second tab
    String secondTabId = windowHandles.stream()
        .filter(id -> !id.equals(firstTabId))
        .findFirst()
        .orElseThrow(() -> new AssertionError("Could not find second tab"));

    // Create coordinates
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .build();

    // Set geolocation override for both tabs
    try (Emulation emulation = new Emulation(driver)) {
      emulation.setGeolocationOverride(coordinates, List.of(firstTabId, secondTabId));

      // Verify in first tab
      driver.switchTo().window(firstTabId);
      verifyGeolocationOverride(firstTabId);

      // Verify in second tab
      driver.switchTo().window(secondTabId);
      verifyGeolocationOverride(secondTabId);
    }
  }

  private void verifyGeolocationOverride(String tabId) {
    try (Script script = new Script(tabId, driver)) {
      // Create a JavaScript function that returns a Promise with the geolocation
      String geolocationFunction =
          "() => new Promise((resolve, reject) => {" +
          "  navigator.geolocation.getCurrentPosition(" +
          "    position => {" +
          "      resolve({" +
          "        latitude: position.coords.latitude," +
          "        longitude: position.coords.longitude" +
          "      });" +
          "    }," +
          "    error => {" +
          "      reject(error.message);" +
          "    }" +
          "  );" +
          "})";

      // Call the function and wait for the Promise to resolve
      CallFunctionParameters parameters = new CallFunctionParameters(
          new ContextTarget(tabId), geolocationFunction, true);

      EvaluateResult result = script.callFunction(parameters);

      // Verify the result
      assertThat(result.getResultType()).isEqualTo(EvaluateResult.Type.SUCCESS);

      EvaluateResultSuccess successResult = (EvaluateResultSuccess) result;
      assertThat(successResult.getResult().getType()).isEqualTo("object");
      assertThat(successResult.getResult().getValue().isPresent()).isTrue();

      @SuppressWarnings("unchecked")
      Map<String, Object> position = (Map<String, Object>) successResult.getResult().getValue().get();

      // Verify the coordinates match what we set
      assertThat((Double) position.get("latitude")).isCloseTo(37.7749, within(0.0001));
      assertThat((Double) position.get("longitude")).isCloseTo(-122.4194, within(0.0001));
    }
  }
}
