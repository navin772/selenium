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

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.openqa.selenium.internal.Require;

/**
 * Parameters for the emulation.setGeolocationOverride command.
 */
public class SetGeolocationOverrideParameters {
  private final Optional<GeolocationCoordinates> coordinates;
  private final Optional<List<String>> contexts;
  private final Optional<List<String>> userContexts;

  private SetGeolocationOverrideParameters(
      Optional<GeolocationCoordinates> coordinates,
      Optional<List<String>> contexts,
      Optional<List<String>> userContexts) {
    
    // Validate that either contexts or userContexts is provided, but not both
    if (contexts.isPresent() && userContexts.isPresent()) {
      throw new IllegalArgumentException("Cannot specify both contexts and userContexts");
    }
    
    if (!contexts.isPresent() && !userContexts.isPresent()) {
      throw new IllegalArgumentException("Either contexts or userContexts must be specified");
    }
    
    this.coordinates = coordinates;
    this.contexts = contexts;
    this.userContexts = userContexts;
  }

  public static Builder builder() {
    return new Builder();
  }

  public Optional<GeolocationCoordinates> getCoordinates() {
    return coordinates;
  }

  public Optional<List<String>> getContexts() {
    return contexts;
  }

  public Optional<List<String>> getUserContexts() {
    return userContexts;
  }

  public Map<String, Object> toMap() {
    Map<String, Object> map = new HashMap<>();
    
    // Handle coordinates - if null, explicitly set to null in the map
    if (coordinates.isPresent()) {
      map.put("coordinates", coordinates.get().toMap());
    } else {
      map.put("coordinates", null);
    }
    
    contexts.ifPresent(value -> map.put("contexts", value));
    userContexts.ifPresent(value -> map.put("userContexts", value));
    
    return map;
  }

  public static class Builder {
    private Optional<GeolocationCoordinates> coordinates = Optional.empty();
    private Optional<List<String>> contexts = Optional.empty();
    private Optional<List<String>> userContexts = Optional.empty();

    public Builder setCoordinates(GeolocationCoordinates coordinates) {
      this.coordinates = Optional.ofNullable(coordinates);
      return this;
    }

    public Builder setContexts(List<String> contexts) {
      this.contexts = Optional.ofNullable(contexts);
      return this;
    }

    public Builder setUserContexts(List<String> userContexts) {
      this.userContexts = Optional.ofNullable(userContexts);
      return this;
    }

    public SetGeolocationOverrideParameters build() {
      return new SetGeolocationOverrideParameters(coordinates, contexts, userContexts);
    }
  }
}