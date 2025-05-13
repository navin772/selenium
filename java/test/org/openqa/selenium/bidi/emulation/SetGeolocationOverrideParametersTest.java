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

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

public class SetGeolocationOverrideParametersTest {

  @Test
  public void testWithCoordinatesAndContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    List<String> contexts = Arrays.asList("context1", "context2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(coordinates)
        .setContexts(contexts)
        .build();
    
    assertThat(parameters.getCoordinates().isPresent()).isTrue();
    assertThat(parameters.getCoordinates().get()).isEqualTo(coordinates);
    assertThat(parameters.getContexts().isPresent()).isTrue();
    assertThat(parameters.getContexts().get()).isEqualTo(contexts);
    assertThat(parameters.getUserContexts().isPresent()).isFalse();
  }

  @Test
  public void testWithCoordinatesAndUserContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    List<String> userContexts = Arrays.asList("userContext1", "userContext2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(coordinates)
        .setUserContexts(userContexts)
        .build();
    
    assertThat(parameters.getCoordinates().isPresent()).isTrue();
    assertThat(parameters.getCoordinates().get()).isEqualTo(coordinates);
    assertThat(parameters.getContexts().isPresent()).isFalse();
    assertThat(parameters.getUserContexts().isPresent()).isTrue();
    assertThat(parameters.getUserContexts().get()).isEqualTo(userContexts);
  }

  @Test
  public void testWithNullCoordinatesAndContexts() {
    List<String> contexts = Arrays.asList("context1", "context2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(null)
        .setContexts(contexts)
        .build();
    
    assertThat(parameters.getCoordinates().isPresent()).isFalse();
    assertThat(parameters.getContexts().isPresent()).isTrue();
    assertThat(parameters.getContexts().get()).isEqualTo(contexts);
    assertThat(parameters.getUserContexts().isPresent()).isFalse();
  }

  @Test
  public void testWithNullCoordinatesAndUserContexts() {
    List<String> userContexts = Arrays.asList("userContext1", "userContext2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(null)
        .setUserContexts(userContexts)
        .build();
    
    assertThat(parameters.getCoordinates().isPresent()).isFalse();
    assertThat(parameters.getContexts().isPresent()).isFalse();
    assertThat(parameters.getUserContexts().isPresent()).isTrue();
    assertThat(parameters.getUserContexts().get()).isEqualTo(userContexts);
  }

  @Test
  public void testToMapWithCoordinatesAndContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    List<String> contexts = Arrays.asList("context1", "context2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(coordinates)
        .setContexts(contexts)
        .build();
    
    Map<String, Object> map = parameters.toMap();
    
    assertThat(map).containsKey("coordinates");
    @SuppressWarnings("unchecked")
    Map<String, Object> coordsMap = (Map<String, Object>) map.get("coordinates");
    assertThat(coordsMap).containsEntry("latitude", 37.7749);
    assertThat(coordsMap).containsEntry("longitude", -122.4194);
    
    assertThat(map).containsKey("contexts");
    @SuppressWarnings("unchecked")
    List<String> contextsList = (List<String>) map.get("contexts");
    assertThat(contextsList).containsExactly("context1", "context2");
    
    assertThat(map).doesNotContainKey("userContexts");
  }

  @Test
  public void testToMapWithCoordinatesAndUserContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    List<String> userContexts = Arrays.asList("userContext1", "userContext2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(coordinates)
        .setUserContexts(userContexts)
        .build();
    
    Map<String, Object> map = parameters.toMap();
    
    assertThat(map).containsKey("coordinates");
    @SuppressWarnings("unchecked")
    Map<String, Object> coordsMap = (Map<String, Object>) map.get("coordinates");
    assertThat(coordsMap).containsEntry("latitude", 37.7749);
    assertThat(coordsMap).containsEntry("longitude", -122.4194);
    
    assertThat(map).doesNotContainKey("contexts");
    
    assertThat(map).containsKey("userContexts");
    @SuppressWarnings("unchecked")
    List<String> userContextsList = (List<String>) map.get("userContexts");
    assertThat(userContextsList).containsExactly("userContext1", "userContext2");
  }

  @Test
  public void testToMapWithNullCoordinatesAndContexts() {
    List<String> contexts = Arrays.asList("context1", "context2");
    
    SetGeolocationOverrideParameters parameters = SetGeolocationOverrideParameters.builder()
        .setCoordinates(null)
        .setContexts(contexts)
        .build();
    
    Map<String, Object> map = parameters.toMap();
    
    assertThat(map).containsKey("coordinates");
    assertThat(map.get("coordinates")).isNull();
    
    assertThat(map).containsKey("contexts");
    @SuppressWarnings("unchecked")
    List<String> contextsList = (List<String>) map.get("contexts");
    assertThat(contextsList).containsExactly("context1", "context2");
    
    assertThat(map).doesNotContainKey("userContexts");
  }

  @Test
  public void testInvalidBothContextsAndUserContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    List<String> contexts = Arrays.asList("context1", "context2");
    List<String> userContexts = Arrays.asList("userContext1", "userContext2");
    
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> SetGeolocationOverrideParameters.builder()
            .setCoordinates(coordinates)
            .setContexts(contexts)
            .setUserContexts(userContexts)
            .build())
        .withMessageContaining("Cannot specify both contexts and userContexts");
  }

  @Test
  public void testInvalidNoContextsOrUserContexts() {
    GeolocationCoordinates coordinates = GeolocationCoordinates.builder()
        .setLatitude(37.7749)
        .setLongitude(-122.4194)
        .build();
    
    assertThatExceptionOfType(IllegalArgumentException.class)
        .isThrownBy(() -> SetGeolocationOverrideParameters.builder()
            .setCoordinates(coordinates)
            .build())
        .withMessageContaining("Either contexts or userContexts must be specified");
  }
}