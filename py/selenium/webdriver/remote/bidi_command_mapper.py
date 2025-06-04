# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""BiDi Command Mapper for WebDriver Classic to BiDi command translation."""

import logging
from typing import Any, Dict, Optional

from selenium.webdriver.common.bidi.storage import (
    BrowsingContextPartitionDescriptor,
    BytesValue,
    CookieFilter,
    PartialCookie,
)
from selenium.webdriver.remote.command import Command

logger = logging.getLogger(__name__)


class BiDiCommandMapper:
    """Maps classic WebDriver commands to BiDi implementations."""

    # Mapping of classic commands to BiDi handler methods
    COMMAND_MAPPINGS = {
        # Navigation commands (browsing_context module)
        Command.GET: "browsing_context_navigate",
        Command.GET_CURRENT_URL: "browsing_context_get_url",
        Command.GO_BACK: "browsing_context_back",
        Command.GO_FORWARD: "browsing_context_forward",
        Command.REFRESH: "browsing_context_reload",
        Command.CLOSE: "browsing_context_close",
        Command.NEW_WINDOW: "browsing_context_create",
        Command.W3C_GET_CURRENT_WINDOW_HANDLE: "browsing_context_get_current_handle",
        Command.W3C_GET_WINDOW_HANDLES: "browsing_context_get_handles",
        Command.SCREENSHOT: "browsing_context_screenshot",
        Command.PRINT_PAGE: "browsing_context_print",

        # Cookie commands (storage module)
        Command.GET_ALL_COOKIES: "storage_get_all_cookies",
        Command.GET_COOKIE: "storage_get_cookie",
        Command.ADD_COOKIE: "storage_add_cookie",
        Command.DELETE_COOKIE: "storage_delete_cookie",
        Command.DELETE_ALL_COOKIES: "storage_delete_all_cookies",

        # Window management commands (browser module)
        Command.GET_WINDOW_RECT: "browser_get_window_rect",
        Command.SET_WINDOW_RECT: "browser_set_window_rect",
        Command.W3C_MAXIMIZE_WINDOW: "browser_maximize_window",
        Command.MINIMIZE_WINDOW: "browser_minimize_window",
        Command.FULLSCREEN_WINDOW: "browser_fullscreen_window",
    }

    def __init__(self, webdriver_instance):
        """Initialize the BiDi command mapper.

        Args:
            webdriver_instance: The WebDriver instance to use for BiDi operations.
        """
        self.driver = webdriver_instance

    def can_execute_with_bidi(self, command: str) -> bool:
        """Check if a command can be executed with BiDi.

        Args:
            command: The WebDriver command to check.

        Returns:
            True if the command can be executed with BiDi, False otherwise.
        """
        in_mappings = command in self.COMMAND_MAPPINGS
        has_websocket = self.driver._websocket_connection is not None
        has_method = hasattr(self, self.COMMAND_MAPPINGS.get(command, "")) if in_mappings else False

        logger.info(f"BiDi capability check for {command}:")
        logger.info(f"  - In command mappings: {in_mappings}")
        logger.info(f"  - Has websocket connection: {has_websocket}")
        logger.info(f"  - Has handler method: {has_method}")

        if in_mappings:
            logger.info(f"  - Maps to method: {self.COMMAND_MAPPINGS[command]}")

        result = in_mappings and has_websocket and has_method
        logger.info(f"  - Final result: {result}")

        return result

    def execute_bidi_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a command using BiDi.

        Args:
            command: The WebDriver command to execute.
            params: Parameters for the command.

        Returns:
            The result of the BiDi command execution.

        Raises:
            NotImplementedError: If the command is not supported by BiDi.
            Exception: If the BiDi command execution fails.
        """
        logger.info(f"=== BiDi Command Mapper: execute_bidi_command for {command} ===")

        if not self.can_execute_with_bidi(command):
            logger.error(f"BiDi mapping not available for command: {command}")
            raise NotImplementedError(f"BiDi mapping not available for command: {command}")

        bidi_method_name = self.COMMAND_MAPPINGS[command]
        bidi_method = getattr(self, bidi_method_name)

        logger.info(f"Executing BiDi command: {command} -> {bidi_method_name}")
        logger.info(f"Parameters: {params}")

        try:
            result = bidi_method(params or {})
            logger.info(f"BiDi command {command} executed successfully")
            logger.info(f"Result: {result}")
            return result
        except Exception as e:
            logger.error(f"BiDi command {command} failed: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def _get_current_context_id(self) -> str:
        """Get the current browsing context ID."""
        try:
            # Get the current context from the browsing context tree
            contexts = self.driver.browsing_context.get_tree()
            if contexts:
                # Return the first context (current window)
                return contexts[0].context
            raise Exception("No browsing context available")
        except Exception as e:
            # Log the error for debugging
            logger.warning(f"Failed to get current context ID: {e}")
            raise

    # Browsing Context Commands

    def browsing_context_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a URL using BiDi."""
        url = params.get("url")
        if not url:
            raise ValueError("URL parameter is required for navigation")

        context_id = self._get_current_context_id()
        result = self.driver.browsing_context.navigate(context=context_id, url=url)

        return {"value": None}  # Classic format expects None for successful navigation

    def browsing_context_get_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current URL using BiDi."""
        context_id = self._get_current_context_id()
        contexts = self.driver.browsing_context.get_tree(root=context_id)

        if contexts:
            return {"value": contexts[0].url}

        raise Exception("Could not retrieve current URL")

    def browsing_context_back(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate back using BiDi."""
        context_id = self._get_current_context_id()
        self.driver.browsing_context.traverse_history(context=context_id, delta=-1)
        return {"value": None}

    def browsing_context_forward(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate forward using BiDi."""
        context_id = self._get_current_context_id()
        self.driver.browsing_context.traverse_history(context=context_id, delta=1)
        return {"value": None}

    def browsing_context_reload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reload page using BiDi."""
        context_id = self._get_current_context_id()
        self.driver.browsing_context.reload(context=context_id)
        return {"value": None}

    def browsing_context_close(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close window using BiDi."""
        context_id = self._get_current_context_id()
        self.driver.browsing_context.close(context=context_id)
        return {"value": None}

    def browsing_context_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new window using BiDi."""
        window_type = params.get("type", "tab")
        context_id = self.driver.browsing_context.create(type=window_type)
        return {"value": {"handle": context_id, "type": window_type}}

    def browsing_context_get_current_handle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current window handle using BiDi."""
        context_id = self._get_current_context_id()
        return {"value": context_id}

    def browsing_context_get_handles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all window handles using BiDi."""
        contexts = self.driver.browsing_context.get_tree()
        handles = [context.context for context in contexts]
        return {"value": handles}

    def browsing_context_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take screenshot using BiDi."""
        context_id = self._get_current_context_id()
        screenshot_data = self.driver.browsing_context.capture_screenshot(context=context_id)
        return {"value": screenshot_data}

    def browsing_context_print(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Print page using BiDi."""
        context_id = self._get_current_context_id()
        pdf_data = self.driver.browsing_context.print(context=context_id)
        return {"value": pdf_data}

    # Storage Commands

    def storage_get_all_cookies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all cookies using BiDi."""
        context_id = self._get_current_context_id()
        partition = BrowsingContextPartitionDescriptor(context=context_id)

        result = self.driver.storage.get_cookies(partition=partition)

        # Convert BiDi cookies to classic format
        classic_cookies = []
        for cookie in result.cookies:
            classic_cookie = {
                "name": cookie.name,
                "value": cookie.value.value,  # Extract string value from BytesValue
                "domain": cookie.domain,
            }

            # Add optional fields if present
            if cookie.path is not None:
                classic_cookie["path"] = cookie.path
            if cookie.secure is not None:
                classic_cookie["secure"] = cookie.secure
            if cookie.http_only is not None:
                classic_cookie["httpOnly"] = cookie.http_only
            if cookie.same_site is not None:
                classic_cookie["sameSite"] = cookie.same_site
            if cookie.expiry is not None:
                classic_cookie["expiry"] = cookie.expiry

            classic_cookies.append(classic_cookie)

        return {"value": classic_cookies}

    def storage_get_cookie(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific cookie using BiDi."""
        cookie_name = params.get("name")
        if not cookie_name:
            raise ValueError("Cookie name is required")

        context_id = self._get_current_context_id()
        partition = BrowsingContextPartitionDescriptor(context=context_id)
        cookie_filter = CookieFilter(name=cookie_name)

        result = self.driver.storage.get_cookies(filter=cookie_filter, partition=partition)

        if result.cookies:
            cookie = result.cookies[0]
            classic_cookie = {
                "name": cookie.name,
                "value": cookie.value.value,
                "domain": cookie.domain,
            }

            # Add optional fields if present
            if cookie.path is not None:
                classic_cookie["path"] = cookie.path
            if cookie.secure is not None:
                classic_cookie["secure"] = cookie.secure
            if cookie.http_only is not None:
                classic_cookie["httpOnly"] = cookie.http_only
            if cookie.same_site is not None:
                classic_cookie["sameSite"] = cookie.same_site
            if cookie.expiry is not None:
                classic_cookie["expiry"] = cookie.expiry

            return {"value": classic_cookie}

        return {"value": None}

    def storage_add_cookie(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a cookie using BiDi."""
        cookie_dict = params.get("cookie", {})

        # Convert classic cookie format to BiDi format
        name = cookie_dict.get("name")
        value = cookie_dict.get("value")
        domain = cookie_dict.get("domain")

        if not all([name, value, domain]):
            raise ValueError("Cookie name, value, and domain are required")

        # Create BytesValue for the cookie value
        bytes_value = BytesValue(BytesValue.TYPE_STRING, value)

        # Create PartialCookie
        partial_cookie = PartialCookie(
            name=name,
            value=bytes_value,
            domain=domain,
            path=cookie_dict.get("path"),
            http_only=cookie_dict.get("httpOnly"),
            secure=cookie_dict.get("secure"),
            same_site=cookie_dict.get("sameSite"),
            expiry=cookie_dict.get("expiry"),
        )

        context_id = self._get_current_context_id()
        partition = BrowsingContextPartitionDescriptor(context=context_id)

        self.driver.storage.set_cookie(cookie=partial_cookie, partition=partition)
        return {"value": None}

    def storage_delete_cookie(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a specific cookie using BiDi."""
        cookie_name = params.get("name")
        if not cookie_name:
            raise ValueError("Cookie name is required")

        context_id = self._get_current_context_id()
        partition = BrowsingContextPartitionDescriptor(context=context_id)
        cookie_filter = CookieFilter(name=cookie_name)

        self.driver.storage.delete_cookies(filter=cookie_filter, partition=partition)
        return {"value": None}

    def storage_delete_all_cookies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete all cookies using BiDi."""
        context_id = self._get_current_context_id()
        partition = BrowsingContextPartitionDescriptor(context=context_id)

        self.driver.storage.delete_cookies(partition=partition)
        return {"value": None}

    # Browser Commands

    def browser_get_window_rect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get window rectangle using BiDi."""
        client_windows = self.driver.browser.get_client_windows()

        # Find the active window
        for window in client_windows:
            if window.is_active():
                return {
                    "value": {
                        "x": window.get_x(),
                        "y": window.get_y(),
                        "width": window.get_width(),
                        "height": window.get_height(),
                    }
                }

        # If no active window found, use the first one
        if client_windows:
            window = client_windows[0]
            return {
                "value": {
                    "x": window.get_x(),
                    "y": window.get_y(),
                    "width": window.get_width(),
                    "height": window.get_height(),
                }
            }

        raise Exception("No client windows available")

    def browser_set_window_rect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set window rectangle using BiDi."""
        # Note: This is a placeholder as browser.setClientWindowState is not fully implemented
        # in the current BiDi browser module. This would need to be added to the browser module.
        raise NotImplementedError("browser.setClientWindowState not yet implemented in BiDi browser module")

    def browser_maximize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Maximize window using BiDi."""
        # Note: This is a placeholder as browser.setClientWindowState is not fully implemented
        raise NotImplementedError("browser.setClientWindowState not yet implemented in BiDi browser module")

    def browser_minimize_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Minimize window using BiDi."""
        # Note: This is a placeholder as browser.setClientWindowState is not fully implemented
        raise NotImplementedError("browser.setClientWindowState not yet implemented in BiDi browser module")

    def browser_fullscreen_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fullscreen window using BiDi."""
        # Note: This is a placeholder as browser.setClientWindowState is not fully implemented
        raise NotImplementedError("browser.setClientWindowState not yet implemented in BiDi browser module")
