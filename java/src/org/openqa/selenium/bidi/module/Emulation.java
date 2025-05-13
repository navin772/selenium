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

package org.openqa.selenium.bidi.module;

import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.bidi.BiDi;
import org.openqa.selenium.bidi.Command;
import org.openqa.selenium.bidi.HasBiDi;
import org.openqa.selenium.bidi.emulation.GeolocationCoordinates;
import org.openqa.selenium.bidi.emulation.SetGeolocationOverrideParameters;
import org.openqa.selenium.internal.Require;

/**
 * The emulation module contains commands relating to emulation of browser APIs.
 */
public class Emulation implements AutoCloseable {
  private final BiDi bidi;
  private final Set<String> browsingContextIds;

  /**
   * Creates a new Emulation module that can interact with any browsing context.
   *
   * @param driver The WebDriver instance
   */
  public Emulation(WebDriver driver) {
    this(new HashSet<>(), driver);
  }

  /**
   * Creates a new Emulation module that will interact with the specified browsing context.
   *
   * @param browsingContextId The browsing context ID
   * @param driver The WebDriver instance
   */
  public Emulation(String browsingContextId, WebDriver driver) {
    this(Collections.singleton(Require.nonNull("Browsing context id", browsingContextId)), driver);
  }

  /**
   * Creates a new Emulation module that will interact with the specified browsing contexts.
   *
   * @param browsingContextIds The set of browsing context IDs
   * @param driver The WebDriver instance
   */
  public Emulation(Set<String> browsingContextIds, WebDriver driver) {
    Require.nonNull("WebDriver", driver);
    Require.nonNull("Browsing context id list", browsingContextIds);

    if (!(driver instanceof HasBiDi)) {
      throw new IllegalArgumentException("WebDriver instance must support BiDi protocol");
    }

    this.bidi = ((HasBiDi) driver).getBiDi();
    this.browsingContextIds = browsingContextIds;
  }

  /**
   * Sets the geolocation override for the specified browsing contexts.
   *
   * @param coordinates The geolocation coordinates to set, or null to clear the override
   * @param contexts The list of browsing context IDs
   */
  public void setGeolocationOverride(GeolocationCoordinates coordinates, List<String> contexts) {
    Map<String, Object> params = new HashMap<>();
    
    if (coordinates != null) {
      params.put("coordinates", coordinates.toMap());
    } else {
      params.put("coordinates", null);
    }
    
    params.put("contexts", contexts);
    
    this.bidi.send(new Command<>("emulation.setGeolocationOverride", params));
  }

  /**
   * Sets the geolocation override for the specified user contexts.
   *
   * @param coordinates The geolocation coordinates to set, or null to clear the override
   * @param userContexts The list of user context IDs
   */
  public void setGeolocationOverrideForUserContexts(GeolocationCoordinates coordinates, List<String> userContexts) {
    Map<String, Object> params = new HashMap<>();
    
    if (coordinates != null) {
      params.put("coordinates", coordinates.toMap());
    } else {
      params.put("coordinates", null);
    }
    
    params.put("userContexts", userContexts);
    
    this.bidi.send(new Command<>("emulation.setGeolocationOverride", params));
  }

  /**
   * Sets the geolocation override for the browsing context specified in the constructor.
   * This method can only be used if the Emulation module was created with a specific browsing context.
   *
   * @param coordinates The geolocation coordinates to set, or null to clear the override
   */
  public void setGeolocationOverride(GeolocationCoordinates coordinates) {
    if (browsingContextIds.isEmpty()) {
      throw new IllegalStateException("No browsing context ID was specified in the constructor");
    }

    setGeolocationOverride(coordinates, List.copyOf(browsingContextIds));
  }

  /**
   * Clears the geolocation override for the specified browsing contexts.
   *
   * @param contexts The list of browsing context IDs
   */
  public void clearGeolocationOverride(List<String> contexts) {
    setGeolocationOverride(null, contexts);
  }

  /**
   * Clears the geolocation override for the specified user contexts.
   *
   * @param userContexts The list of user context IDs
   */
  public void clearGeolocationOverrideForUserContexts(List<String> userContexts) {
    setGeolocationOverrideForUserContexts(null, userContexts);
  }

  /**
   * Clears the geolocation override for the browsing context specified in the constructor.
   * This method can only be used if the Emulation module was created with a specific browsing context.
   */
  public void clearGeolocationOverride() {
    if (browsingContextIds.isEmpty()) {
      throw new IllegalStateException("No browsing context ID was specified in the constructor");
    }

    clearGeolocationOverride(List.copyOf(browsingContextIds));
  }

  /**
   * Closes this resource, relinquishing any underlying resources.
   * This method is invoked automatically on objects managed by the
   * try-with-resources statement.
   */
  @Override
  public void close() {
    // No resources to clean up for now
  }
}