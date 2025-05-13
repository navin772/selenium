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
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

import java.util.Map;

import org.junit.jupiter.api.Test;

public class GeolocationCoordinatesTest {

  @Test
  public void testValidCoordinates() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .setAltitude(10.0)
        .setAltitudeAccuracy(5.0)
        .setHeading(90.0)
        .setSpeed(5.0)
        .build();

    assertThat(coordinates.getLatitude()).isEqualTo(37.7749);
    assertThat(coordinates.getLongitude()).isEqualTo(-122.4194);
    assertThat(coordinates.getAccuracy()).isEqualTo(100.0);
    assertThat(coordinates.getAltitude().isPresent()).isTrue();
    assertThat(coordinates.getAltitude().get()).isEqualTo(10.0);
    assertThat(coordinates.getAltitudeAccuracy().isPresent()).isTrue();
    assertThat(coordinates.getAltitudeAccuracy().get()).isEqualTo(5.0);
    assertThat(coordinates.getHeading().isPresent()).isTrue();
    assertThat(coordinates.getHeading().get()).isEqualTo(90.0);
    assertThat(coordinates.getSpeed().isPresent()).isTrue();
    assertThat(coordinates.getSpeed().get()).isEqualTo(5.0);
  }

  @Test
  public void testMinimalCoordinates() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();

    assertThat(coordinates.getLatitude()).isEqualTo(37.7749);
    assertThat(coordinates.getLongitude()).isEqualTo(-122.4194);
    assertThat(coordinates.getAccuracy()).isEqualTo(1.0); // Default value
    assertThat(coordinates.getAltitude().isPresent()).isFalse();
    assertThat(coordinates.getAltitudeAccuracy().isPresent()).isFalse();
    assertThat(coordinates.getHeading().isPresent()).isFalse();
    assertThat(coordinates.getSpeed().isPresent()).isFalse();
  }

  @Test
  public void testToMap() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .setAccuracy(100.0)
        .setAltitude(10.0)
        .setAltitudeAccuracy(5.0)
        .setHeading(90.0)
        .setSpeed(5.0)
        .build();

    Map<String, Object> map = coordinates.toMap();
    
    assertThat(map).containsEntry("latitude", 37.7749);
    assertThat(map).containsEntry("longitude", -122.4194);
    assertThat(map).containsEntry("accuracy", 100.0);
    assertThat(map).containsEntry("altitude", 10.0);
    assertThat(map).containsEntry("altitudeAccuracy", 5.0);
    assertThat(map).containsEntry("heading", 90.0);
    assertThat(map).containsEntry("speed", 5.0);
  }

  @Test
  public void testMinimalToMap() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();

    Map<String, Object> map = coordinates.toMap();
    
    assertThat(map).containsEntry("latitude", 37.7749);
    assertThat(map).containsEntry("longitude", -122.4194);
    assertThat(map).containsEntry("accuracy", 1.0);
    assertThat(map).doesNotContainKey("altitude");
    assertThat(map).doesNotContainKey("altitudeAccuracy");
    assertThat(map).doesNotContainKey("heading");
    assertThat(map).doesNotContainKey("speed");
  }

  @Test
  public void testInvalidLatitude() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(100.0) // Invalid: > 90.0
            .setLongitude(-122.4194)
            .build())
        .withMessageContaining("Latitude must be between -90.0 and 90.0");

    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(-100.0) // Invalid: < -90.0
            .setLongitude(-122.4194)
            .build())
        .withMessageContaining("Latitude must be between -90.0 and 90.0");
  }

  @Test
  public void testInvalidLongitude() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(200.0) // Invalid: > 180.0
            .build())
        .withMessageContaining("Longitude must be between -180.0 and 180.0");

    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-200.0) // Invalid: < -180.0
            .build())
        .withMessageContaining("Longitude must be between -180.0 and 180.0");
  }

  @Test
  public void testInvalidAccuracy() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setAccuracy(-1.0) // Invalid: negative
            .build())
        .withMessageContaining("Accuracy must be non-negative");
  }

  @Test
  public void testInvalidAltitudeAccuracy() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setAltitude(10.0)
            .setAltitudeAccuracy(-1.0) // Invalid: negative
            .build())
        .withMessageContaining("Altitude accuracy must be non-negative");
  }

  @Test
  public void testInvalidHeading() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setHeading(400.0) // Invalid: > 360.0
            .build())
        .withMessageContaining("Heading must be between 0.0 and 360.0");

    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setHeading(-10.0) // Invalid: < 0.0
            .build())
        .withMessageContaining("Heading must be between 0.0 and 360.0");
  }

  @Test
  public void testInvalidSpeed() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setSpeed(-1.0) // Invalid: negative
            .build())
        .withMessageContaining("Speed must be non-negative");
  }

  @Test
  public void testAltitudeAccuracyWithoutAltitude() {
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> GeolocationCoordinates.builder()
            .setLatitude(37.7749)
            .setLongitude(-122.4194)
            .setAltitudeAccuracy(5.0) // Invalid: altitude not provided
            .build())
        .withMessageContaining("Altitude must be provided when altitude accuracy is provided");
  }
}