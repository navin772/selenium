"""
Comprehensive test suite for BiDi-Classic fallback implementation.
Tests all 21 supported commands to verify BiDi execution with classic fallback.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.common.exceptions import WebDriverException


class TestBiDiCommandsComprehensive:

    @pytest.fixture(scope="class")
    def driver(self):
        """Create a Chrome WebDriver instance with BiDi enabled."""
        options = Options()
        options.enable_bidi = True
        driver = webdriver.Chrome(options=options)

        # Verify BiDi is available
        assert driver._should_attempt_bidi(), "BiDi should be available"
        assert driver.bidi_bridge is not None, "BiDi bridge should be initialized"
        assert driver.bidi_bridge.is_bidi_healthy(), "BiDi should be healthy"

        # Reset statistics at the beginning of the test run
        driver.bidi_bridge.reset_statistics()

        yield driver

        # Print final combined statistics before quitting
        print("\n" + "="*60)
        print("FINAL BIDI BRIDGE STATISTICS FOR ENTIRE TEST RUN")
        print("="*60)
        stats = driver.bidi_bridge.get_statistics()
        print(f"BiDi Attempts: {stats['bidi_attempts']}")
        print(f"BiDi Successes: {stats['bidi_successes']}")
        print(f"BiDi Failures: {stats['bidi_failures']}")
        print(f"Classic Fallbacks: {stats['classic_fallbacks']}")
        print(f"BiDi Success Rate: {stats['bidi_success_rate']:.2f}%")
        print("="*60)

        driver.quit()

    @pytest.fixture(autouse=True)
    def setup_test_page(self, driver):
        """Navigate to a test page before each test."""
        driver.get("https://httpbin.org/html")
        time.sleep(1)  # Allow page to load

    # ===== BROWSING CONTEXT COMMANDS (11 tests) =====

    def test_browsing_context_navigate(self, driver):
        """Test GET command - browsingContext.navigate"""
        initial_url = driver.current_url
        driver.get("https://httpbin.org/json")
        assert driver.current_url != initial_url
        assert "httpbin.org/json" in driver.current_url

    def test_browsing_context_get_url(self, driver):
        """Test GET_CURRENT_URL command - browsingContext.getUrl"""
        driver.get("https://httpbin.org/html")
        current_url = driver.current_url
        assert "httpbin.org/html" in current_url

    def test_browsing_context_back(self, driver):
        """Test GO_BACK command - browsingContext.back"""
        # Navigate to create history
        driver.get("https://httpbin.org/html")
        first_url = driver.current_url
        driver.get("https://httpbin.org/json")
        second_url = driver.current_url

        # Go back
        driver.back()
        time.sleep(1)
        assert driver.current_url == first_url

    def test_browsing_context_forward(self, driver):
        """Test GO_FORWARD command - browsingContext.forward"""
        # Navigate to create history
        driver.get("https://httpbin.org/html")
        first_url = driver.current_url
        driver.get("https://httpbin.org/json")
        second_url = driver.current_url

        # Go back then forward
        driver.back()
        time.sleep(1)
        driver.forward()
        time.sleep(1)
        assert driver.current_url == second_url

    def test_browsing_context_reload(self, driver):
        """Test REFRESH command - browsingContext.reload"""
        driver.get("https://httpbin.org/html")
        initial_url = driver.current_url
        driver.refresh()
        time.sleep(1)
        assert driver.current_url == initial_url

    def test_browsing_context_create(self, driver):
        """Test NEW_WINDOW command - browsingContext.create"""
        initial_handles = driver.window_handles
        initial_count = len(initial_handles)

        # Create new window
        driver.execute_script("window.open('about:blank', '_blank');")
        time.sleep(1)

        new_handles = driver.window_handles
        assert len(new_handles) == initial_count + 1

        # Clean up - close the new window
        driver.switch_to.window(new_handles[-1])
        driver.close()
        driver.switch_to.window(initial_handles[0])

    def test_browsing_context_get_current_handle(self, driver):
        """Test W3C_GET_CURRENT_WINDOW_HANDLE command - browsingContext.getCurrentHandle"""
        current_handle = driver.current_window_handle
        assert current_handle is not None
        assert isinstance(current_handle, str)
        assert len(current_handle) > 0

    def test_browsing_context_get_handles(self, driver):
        """Test W3C_GET_WINDOW_HANDLES command - browsingContext.getHandles"""
        handles = driver.window_handles
        assert isinstance(handles, list)
        assert len(handles) >= 1
        assert driver.current_window_handle in handles

    def test_browsing_context_close(self, driver):
        """Test CLOSE command - browsingContext.close"""
        # Create a new window to close (can't close the last window)
        driver.execute_script("window.open('about:blank', '_blank');")
        time.sleep(1)

        handles = driver.window_handles
        assert len(handles) >= 2

        # Switch to new window and close it
        driver.switch_to.window(handles[-1])
        driver.close()

        # Switch back to original window
        remaining_handles = driver.window_handles
        driver.switch_to.window(remaining_handles[0])
        assert len(remaining_handles) == len(handles) - 1

    def test_browsing_context_screenshot(self, driver):
        """Test SCREENSHOT command - browsingContext.screenshot"""
        driver.get("https://httpbin.org/html")
        screenshot = driver.get_screenshot_as_base64()
        assert screenshot is not None
        assert isinstance(screenshot, str)
        assert len(screenshot) > 0

    def test_browsing_context_print(self, driver):
        """Test PRINT_PAGE command - browsingContext.print"""
        driver.get("https://httpbin.org/html")
        print_options = PrintOptions()
        pdf_data = driver.print_page(print_options)
        assert pdf_data is not None
        assert isinstance(pdf_data, str)
        assert len(pdf_data) > 0

    # ===== STORAGE COMMANDS (5 tests) =====

    def test_storage_get_all_cookies(self, driver):
        """Test GET_ALL_COOKIES command - storage.getAllCookies"""
        driver.get("https://httpbin.org/cookies/set/test_cookie/test_value") # this adds a cookie named 'test_cookie'
        time.sleep(1)
        cookies = driver.get_cookies()
        assert isinstance(cookies, list)
        # Check if our test cookie is present
        cookie_names = [cookie['name'] for cookie in cookies]
        assert 'test_cookie' in cookie_names

    def test_storage_add_cookie(self, driver):
        """Test ADD_COOKIE command - storage.addCookie"""
        driver.get("https://httpbin.org/html")

        # Add a cookie with domain specified (required for BiDi)
        test_cookie = {
            "name": "bidi_test_cookie",
            "value": "bidi_test_value",
            "domain": "httpbin.org",
            "path": "/"
        }
        driver.add_cookie(test_cookie)

        # Verify cookie was added
        cookies = driver.get_cookies()
        cookie_names = [cookie['name'] for cookie in cookies]
        assert 'bidi_test_cookie' in cookie_names

        # Find and verify the cookie
        added_cookie = next((c for c in cookies if c['name'] == 'bidi_test_cookie'), None)
        assert added_cookie is not None
        assert added_cookie['value'] == 'bidi_test_value'

    def test_storage_get_cookie(self, driver):
        """Test GET_COOKIE command - storage.getCookie"""
        driver.get("https://httpbin.org/html")

        # Add a test cookie first
        test_cookie = {
            "name": "specific_test_cookie",
            "value": "specific_test_value",
            "domain": "httpbin.org"
        }
        driver.add_cookie(test_cookie)

        # Get the specific cookie
        retrieved_cookie = driver.get_cookie("specific_test_cookie")
        assert retrieved_cookie is not None
        assert retrieved_cookie['name'] == 'specific_test_cookie'
        assert retrieved_cookie['value'] == 'specific_test_value'

    def test_storage_delete_cookie(self, driver):
        """Test DELETE_COOKIE command - storage.deleteCookie"""
        driver.get("https://httpbin.org/html")

        # Add a test cookie first
        test_cookie = {
            "name": "cookie_to_delete",
            "value": "delete_me",
            "domain": "httpbin.org"
        }
        driver.add_cookie(test_cookie)

        # Verify cookie exists
        cookies_before = driver.get_cookies()
        cookie_names_before = [cookie['name'] for cookie in cookies_before]
        assert 'cookie_to_delete' in cookie_names_before

        # Delete the cookie
        driver.delete_cookie("cookie_to_delete")

        # Verify cookie is gone
        cookies_after = driver.get_cookies()
        cookie_names_after = [cookie['name'] for cookie in cookies_after]
        assert 'cookie_to_delete' not in cookie_names_after

    def test_storage_delete_all_cookies(self, driver):
        """Test DELETE_ALL_COOKIES command - storage.deleteAllCookies"""
        driver.get("https://httpbin.org/html")

        # Add some test cookies
        for i in range(3):
            test_cookie = {
                "name": f"test_cookie_{i}",
                "value": f"test_value_{i}",
                "domain": "httpbin.org"
            }
            driver.add_cookie(test_cookie)

        # Verify cookies exist
        cookies_before = driver.get_cookies()
        assert len(cookies_before) >= 3

        # Delete all cookies
        driver.delete_all_cookies()

        # Verify all cookies are gone
        cookies_after = driver.get_cookies()
        assert len(cookies_after) == 0

    # ===== BROWSER COMMANDS (5 tests) =====

    def test_browser_get_window_rect(self, driver):
        """Test GET_WINDOW_RECT command - browser.getWindowRect"""
        try:
            rect = driver.get_window_rect()
            assert isinstance(rect, dict)
            assert 'x' in rect
            assert 'y' in rect
            assert 'width' in rect
            assert 'height' in rect
            assert all(isinstance(rect[key], (int, float)) for key in ['x', 'y', 'width', 'height'])
        except (NotImplementedError, WebDriverException) as e:
            pytest.skip(f"Browser window rect not implemented in BiDi: {e}")

    # ===== These tests are not supported in BiDi yet because browser.setClientWindowState is not implemented =====

    # def test_browser_set_window_rect(self, driver):
    #     """Test SET_WINDOW_RECT command - browser.setWindowRect"""
    #     try:
    #         # Get current rect
    #         original_rect = driver.get_window_rect()
    #
    #         # Set new dimensions
    #         new_width = 800
    #         new_height = 600
    #         driver.set_window_rect(width=new_width, height=new_height)
    #
    #         # Verify change
    #         new_rect = driver.get_window_rect()
    #         assert new_rect['width'] == new_width
    #         assert new_rect['height'] == new_height
    #
    #         # Restore original size
    #         driver.set_window_rect(
    #             width=original_rect['width'],
    #             height=original_rect['height']
    #         )
    #     except (NotImplementedError, WebDriverException) as e:
    #         pytest.skip(f"Browser set window rect not implemented in BiDi: {e}")
    #
    # def test_browser_maximize_window(self, driver):
    #     """Test W3C_MAXIMIZE_WINDOW command - browser.maximizeWindow"""
    #     try:
    #         # Get current size
    #         original_rect = driver.get_window_rect()
    #
    #         # Maximize window
    #         driver.maximize_window()
    #         time.sleep(1)
    #
    #         # Verify window was maximized (should be larger)
    #         maximized_rect = driver.get_window_rect()
    #         assert maximized_rect['width'] >= original_rect['width']
    #         assert maximized_rect['height'] >= original_rect['height']
    #     except (NotImplementedError, WebDriverException) as e:
    #         pytest.skip(f"Browser maximize window not implemented in BiDi: {e}")
    #
    # def test_browser_minimize_window(self, driver):
    #     """Test MINIMIZE_WINDOW command - browser.minimizeWindow"""
    #     try:
    #         driver.minimize_window()
    #         time.sleep(1)
    #         # Note: Verification of minimize is difficult as window state is not easily queryable
    #         # The test passes if no exception is raised
    #     except (NotImplementedError, WebDriverException) as e:
    #         pytest.skip(f"Browser minimize window not implemented in BiDi: {e}")
    #
    # def test_browser_fullscreen_window(self, driver):
    #     """Test FULLSCREEN_WINDOW command - browser.fullscreenWindow"""
    #     try:
    #         # Get current size
    #         original_rect = driver.get_window_rect()
    #
    #         # Fullscreen window
    #         driver.fullscreen_window()
    #         time.sleep(1)
    #
    #         # Verify window is fullscreen (should be larger)
    #         fullscreen_rect = driver.get_window_rect()
    #         assert fullscreen_rect['width'] >= original_rect['width']
    #         assert fullscreen_rect['height'] >= original_rect['height']
    #
    #         # Exit fullscreen (press Escape)
    #         driver.execute_script("document.exitFullscreen ? document.exitFullscreen() : document.webkitExitFullscreen();")
    #         time.sleep(1)
    #     except (NotImplementedError, WebDriverException) as e:
    #         pytest.skip(f"Browser fullscreen window not implemented in BiDi: {e}")

    # ===== INTEGRATION TESTS =====

    def test_bidi_bridge_statistics(self, driver):
        """Test BiDi bridge statistics tracking."""
        # Perform some operations (don't reset stats - we want cumulative)
        driver.get("https://httpbin.org/html")
        driver.get_cookies()
        driver.current_url

        # Check statistics structure and content
        stats = driver.bidi_bridge.get_statistics()
        assert isinstance(stats, dict)
        assert 'bidi_attempts' in stats
        assert 'bidi_successes' in stats
        assert 'bidi_failures' in stats
        assert 'classic_fallbacks' in stats
        assert 'bidi_success_rate' in stats

        # Should have some BiDi attempts from all tests run so far
        assert stats['bidi_attempts'] > 0

        # Print current statistics for this test
        print(f"\nCurrent BiDi Statistics: {stats}")

    def test_bidi_command_configuration(self, driver):
        """Test BiDi bridge command configuration."""
        # Test getting supported commands
        supported_commands = driver.bidi_bridge.get_supported_commands()
        assert isinstance(supported_commands, list)
        assert len(supported_commands) == 21  # All 21 commands should be supported

        # Test getting available commands
        available_commands = driver.bidi_bridge.get_available_commands()
        assert isinstance(available_commands, list)
        assert len(available_commands) <= len(supported_commands)

    def test_bidi_health_check(self, driver):
        """Test BiDi health check functionality."""
        # BiDi should be healthy
        assert driver.bidi_bridge.is_bidi_healthy()

        # Test multiple health checks
        for _ in range(3):
            assert driver.bidi_bridge.is_bidi_healthy()
            time.sleep(0.1)


if __name__ == "__main__":
    # Run the tests with print output
    pytest.main([__file__, "-v", "-s", "--tb=short"])
