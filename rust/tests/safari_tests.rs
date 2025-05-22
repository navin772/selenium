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

use crate::common::get_selenium_manager;

use std::env::consts::OS;

mod common;

#[test]
fn safari_test() {
    let mut cmd = get_selenium_manager();
    let safari_assert = cmd.args(["--browser", "safari"]).assert();

    if OS.eq("macos") {
        safari_assert.success();
    } else {
        safari_assert.failure();
    }
}

#[test]
fn safari_non_macos_safety_test() {
    if !OS.eq("macos") {
        // Test for proper error message with --browser safari
        let mut cmd = get_selenium_manager();
        let output = cmd
            .args(["--browser", "safari"])
            .output()
            .expect("Failed to execute command");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(stderr.contains("Safari is only available on macOS systems"));

        // Test for proper error message with --driver safaridriver
        let mut cmd = get_selenium_manager();
        let output = cmd
            .args(["--driver", "safaridriver"])
            .output()
            .expect("Failed to execute command");
        let stderr = String::from_utf8_lossy(&output.stderr);
        assert!(stderr.contains("safaridriver is only available on macOS systems"));

        // Test that no system directory locks are attempted (with --debug to see detailed logs)
        let mut cmd = get_selenium_manager();
        let output = cmd
            .args(["--browser", "safari", "--debug"])
            .output()
            .expect("Failed to execute command");
        let stderr_str = String::from_utf8_lossy(&output.stderr);

        // Verify we're not seeing any attempt to acquire lock in /bin/ or /usr/bin/
        assert!(!stderr_str.contains("Acquiring lock: /bin/"));
        assert!(!stderr_str.contains("Acquiring lock: /usr/bin/"));
    }
}
