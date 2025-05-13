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
import java.util.Map;
import java.util.Optional;

import org.openqa.selenium.internal.Require;

/**
 * Represents geolocation coordinates for the emulation.setGeolocationOverride command.
 */
public class GeolocationCoordinates {
  private final double latitude;
  private final double longitude;
  private final double accuracy;
  private final Optional<Double> altitude;
  private final Optional<Double> altitudeAccuracy;
  private final Optional<Double> heading;
  private final Optional<Double> speed;

  private GeolocationCoordinates(
      double latitude,
      double longitude,
      double accuracy,
      Optional<Double> altitude,
      Optional<Double> altitudeAccuracy,
      Optional<Double> heading,
      Optional<Double> speed) {
    
    // Validate latitude range (-90.0 to 90.0)
    if (latitude < -90.0 || latitude > 90.0) {
      throw new IllegalArgumentException("Latitude must be between -90.0 and 90.0");
    }
    
    // Validate longitude range (-180.0 to 180.0)
    if (longitude < -180.0 || longitude > 180.0) {
      throw new IllegalArgumentException("Longitude must be between -180.0 and 180.0");
    }
    
    // Validate accuracy is non-negative
    if (accuracy < 0.0) {
      throw new IllegalArgumentException("Accuracy must be non-negative");
    }
    
    // Validate altitudeAccuracy is non-negative if present
    if (altitudeAccuracy.isPresent() && altitudeAccuracy.get() < 0.0) {
      throw new IllegalArgumentException("Altitude accuracy must be non-negative");
    }
    
    // Validate heading range (0.0 to 360.0) if present
    if (heading.isPresent() && (heading.get() < 0.0 || heading.get() > 360.0)) {
      throw new IllegalArgumentException("Heading must be between 0.0 and 360.0");
    }
    
    // Validate speed is non-negative if present
    if (speed.isPresent() && speed.get() < 0.0) {
      throw new IllegalArgumentException("Speed must be non-negative");
    }
    
    // Validate that altitude is present if altitudeAccuracy is present
    if (altitudeAccuracy.isPresent() && !altitude.isPresent()) {
      throw new IllegalArgumentException("Altitude must be provided when altitude accuracy is provided");
    }
    
    this.latitude = latitude;
    this.longitude = longitude;
    this.accuracy = accuracy;
    this.altitude = altitude;
    this.altitudeAccuracy = altitudeAccuracy;
    this.heading = heading;
    this.speed = speed;
  }

  public static Builder builder() {
    return new Builder();
  }

  public double getLatitude() {
    return latitude;
  }

  public double getLongitude() {
    return longitude;
  }

  public double getAccuracy() {
    return accuracy;
  }

  public Optional<Double> getAltitude() {
    return altitude;
  }

  public Optional<Double> getAltitudeAccuracy() {
    return altitudeAccuracy;
  }

  public Optional<Double> getHeading() {
    return heading;
  }

  public Optional<Double> getSpeed() {
    return speed;
  }

  public Map<String, Object> toMap() {
    Map<String, Object> map = new HashMap<>();
    map.put("latitude", latitude);
    map.put("longitude", longitude);
    map.put("accuracy", accuracy);
    
    altitude.ifPresent(value -> map.put("altitude", value));
    altitudeAccuracy.ifPresent(value -> map.put("altitudeAccuracy", value));
    heading.ifPresent(value -> map.put("heading", value));
    speed.ifPresent(value -> map.put("speed", value));
    
    return map;
  }

  public static class Builder {
    private double latitude;
    private double longitude;
    private double accuracy = 1.0; // Default value as per spec
    private Optional<Double> altitude = Optional.empty();
    private Optional<Double> altitudeAccuracy = Optional.empty();
    private Optional<Double> heading = Optional.empty();
    private Optional<Double> speed = Optional.empty();

    public Builder setLatitude(double latitude) {
      this.latitude = latitude;
      return this;
    }

    public Builder setLongitude(double longitude) {
      this.longitude = longitude;
      return this;
    }

    public Builder setAccuracy(double accuracy) {
      this.accuracy = accuracy;
      return this;
    }

    public Builder setAltitude(Double altitude) {
      this.altitude = Optional.ofNullable(altitude);
      return this;
    }

    public Builder setAltitudeAccuracy(Double altitudeAccuracy) {
      this.altitudeAccuracy = Optional.ofNullable(altitudeAccuracy);
      return this;
    }

    public Builder setHeading(Double heading) {
      this.heading = Optional.ofNullable(heading);
      return this;
    }

    public Builder setSpeed(Double speed) {
      this.speed = Optional.ofNullable(speed);
      return this;
    }

    public GeolocationCoordinates build() {
      return new GeolocationCoordinates(
          latitude,
          longitude,
          accuracy,
          altitude,
          altitudeAccuracy,
          heading,
          speed);
    }
  }
}