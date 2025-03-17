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

/**
 * @fileoverview Defines a {@linkplain Driver WebDriver} client for the Chrome Beta browser.
 * This is the same as standard Chrome, but allows configuring Chrome Beta installation.
 */

'use strict'

const chrome = require('./chrome')
const { Browser } = require('./lib/capabilities')

/**
 * Class for managing ChromeDriver specific options for Chrome Beta.
 */
class Options extends chrome.Options {
  /**
   * @param {(Capabilities|Map<string, ?>|Object)=} other Another set of
   *     capabilities to initialize this instance from.
   */
  constructor(other = undefined) {
    super(other)
  }

  /**
   * Sets the path to the Chrome Beta binary to use. On Mac OS X, this path should
   * reference the actual Chrome executable, not just the application binary
   * (e.g. "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta").
   *
   * @param {string} path The path to the Chrome Beta binary to use.
   * @return {!Options} A self reference.
   */
  setChromeBetaBinaryPath(path) {
    return this.setBinaryPath(path)
  }
}

/**
 * Creates a new WebDriver client for Chrome Beta.
 */
class Driver extends chrome.Driver {
  /**
   * @return {chrome.ServiceBuilder} A new service builder instance.
   */
  static getDefaultService() {
    return new chrome.ServiceBuilder().build()
  }
}

Options.prototype.BROWSER_NAME_VALUE = Browser.CHROME
Options.prototype.CAPABILITY_KEY = 'goog:chromeOptions'

// PUBLIC API
module.exports = {
  Driver,
  Options,
  ServiceBuilder: chrome.ServiceBuilder,
}
