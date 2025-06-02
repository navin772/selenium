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

"""BiDi Bridge for orchestrating BiDi-first command execution with classic fallback."""

import logging
from typing import Any, Dict, Optional, Set

from selenium.webdriver.remote.bidi_command_mapper import BiDiCommandMapper

logger = logging.getLogger(__name__)


class BiDiBridge:
    """Orchestrates BiDi-first command execution with classic fallback."""

    def __init__(self, webdriver_instance):
        """Initialize the BiDi bridge.
        
        Args:
            webdriver_instance: The WebDriver instance to use for command execution.
        """
        self.driver = webdriver_instance
        self.mapper = BiDiCommandMapper(webdriver_instance)
        self._disabled_commands: Set[str] = set()
        self._debug_logging = False
        
        # Statistics for monitoring
        self._bidi_attempts = 0
        self._bidi_successes = 0
        self._bidi_failures = 0
        self._classic_fallbacks = 0

    def execute_with_fallback(self, command: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute command with BiDi-first, classic fallback strategy.
        
        Args:
            command: The WebDriver command to execute.
            params: Parameters for the command.
            
        Returns:
            The result of the command execution.
        """
        params = params or {}
        logger.info(f"=== BiDi Bridge: execute_with_fallback for command: {command} ===")
        
        # Check if BiDi should be attempted for this command
        if self._should_use_bidi(command):
            try:
                self._bidi_attempts += 1
                logger.info(f"Attempting BiDi execution for command: {command}")
                
                result = self.mapper.execute_bidi_command(command, params)
                self._bidi_successes += 1
                
                logger.info(f"BiDi execution successful for command: {command}")
                
                return result
                
            except Exception as e:
                self._bidi_failures += 1
                self._log_bidi_fallback(command, e)
                
                # Continue to classic fallback
        else:
            logger.info(f"BiDi not used for command: {command}, falling back to classic")
        
        # Execute with classic WebDriver protocol
        logger.info(f"Executing command {command} with classic protocol")
        return self._execute_classic(command, params)

    def _should_use_bidi(self, command: str) -> bool:
        """Determine if BiDi should be attempted for this command.
        
        Args:
            command: The WebDriver command to check.
            
        Returns:
            True if BiDi should be attempted, False otherwise.
        """
        logger.info(f"=== Checking if should use BiDi for command: {command} ===")
        
        # Check each condition individually
        command_not_disabled = command not in self._disabled_commands
        bidi_available = self._is_bidi_available()
        can_execute = self.mapper.can_execute_with_bidi(command)
        is_healthy = self.is_bidi_healthy()
        
        logger.info(f"Command not disabled: {command_not_disabled}")
        logger.info(f"BiDi available: {bidi_available}")
        logger.info(f"Can execute with BiDi: {can_execute}")
        logger.info(f"BiDi is healthy: {is_healthy}")
        
        should_use = command_not_disabled and bidi_available and can_execute and is_healthy
        logger.info(f"Final decision - should use BiDi: {should_use}")
        
        return should_use

    def _is_bidi_available(self) -> bool:
        """Check if BiDi is available for this session.
        
        Returns:
            True if BiDi is available, False otherwise.
        """
        return (
            self.driver.caps.get("webSocketUrl") is not None
            and self.driver._websocket_connection is not None
        )

    def _execute_classic(self, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command using classic WebDriver protocol.
        
        Args:
            command: The WebDriver command to execute.
            params: Parameters for the command.
            
        Returns:
            The result of the classic command execution.
        """
        self._classic_fallbacks += 1
        
        if self._debug_logging:
            logger.info(f"Executing command with classic protocol: {command}")
        
        # Prepare parameters for classic execution
        wrapped_params = self.driver._wrap_value(params)
        
        if self.driver.session_id:
            if not wrapped_params:
                wrapped_params = {"sessionId": self.driver.session_id}
            elif "sessionId" not in wrapped_params:
                wrapped_params["sessionId"] = self.driver.session_id

        # Execute using the original command executor
        response = self.driver.command_executor.execute(command, wrapped_params)
        
        if response:
            self.driver.error_handler.check_response(response)
            response["value"] = self.driver._unwrap_value(response.get("value", None))
            return response
        
        # If the server doesn't send a response, assume success
        return {"success": 0, "value": None, "sessionId": self.driver.session_id}

    def _log_bidi_fallback(self, command: str, error: Exception) -> None:
        """Log BiDi fallback information.
        
        Args:
            command: The command that failed with BiDi.
            error: The exception that occurred.
        """
        if self._debug_logging:
            logger.warning(f"BiDi command {command} failed, falling back to classic: {error}")
        else:
            logger.debug(f"BiDi command {command} failed, falling back to classic: {error}")

    # Configuration methods

    def disable_bidi_for_command(self, command: str) -> None:
        """Disable BiDi execution for a specific command.
        
        Args:
            command: The command to disable BiDi for.
        """
        self._disabled_commands.add(command)
        logger.info(f"BiDi disabled for command: {command}")

    def enable_bidi_for_command(self, command: str) -> None:
        """Re-enable BiDi execution for a specific command.
        
        Args:
            command: The command to re-enable BiDi for.
        """
        self._disabled_commands.discard(command)
        logger.info(f"BiDi re-enabled for command: {command}")

    def disable_bidi_for_commands(self, commands: list[str]) -> None:
        """Disable BiDi execution for multiple commands.
        
        Args:
            commands: List of commands to disable BiDi for.
        """
        for command in commands:
            self.disable_bidi_for_command(command)

    def enable_debug_logging(self) -> None:
        """Enable debug logging for BiDi operations."""
        self._debug_logging = True
        logger.info("BiDi debug logging enabled")

    def disable_debug_logging(self) -> None:
        """Disable debug logging for BiDi operations."""
        self._debug_logging = False
        logger.info("BiDi debug logging disabled")

    def get_disabled_commands(self) -> Set[str]:
        """Get the set of commands that have BiDi disabled.
        
        Returns:
            Set of disabled command names.
        """
        return self._disabled_commands.copy()

    def clear_disabled_commands(self) -> None:
        """Clear all disabled commands, re-enabling BiDi for all supported commands."""
        self._disabled_commands.clear()
        logger.info("All BiDi command restrictions cleared")

    # Statistics and monitoring

    def get_statistics(self) -> Dict[str, int]:
        """Get BiDi usage statistics.
        
        Returns:
            Dictionary containing usage statistics.
        """
        return {
            "bidi_attempts": self._bidi_attempts,
            "bidi_successes": self._bidi_successes,
            "bidi_failures": self._bidi_failures,
            "classic_fallbacks": self._classic_fallbacks,
            "bidi_success_rate": (
                self._bidi_successes / self._bidi_attempts * 100
                if self._bidi_attempts > 0
                else 0
            ),
        }

    def reset_statistics(self) -> None:
        """Reset all usage statistics."""
        self._bidi_attempts = 0
        self._bidi_successes = 0
        self._bidi_failures = 0
        self._classic_fallbacks = 0
        logger.info("BiDi statistics reset")

    def log_statistics(self) -> None:
        """Log current usage statistics."""
        stats = self.get_statistics()
        logger.info(f"BiDi Bridge Statistics: {stats}")

    # Health check methods

    def is_bidi_healthy(self) -> bool:
        """Check if BiDi connection is healthy.
        
        Returns:
            True if BiDi is available and working, False otherwise.
        """
        logger.info("=== BiDi Health Check Debug ===")
        
        # Check basic availability first
        if not self._is_bidi_available():
            logger.warning("BiDi not available - basic availability check failed")
            logger.info(f"webSocketUrl in caps: {self.driver.caps.get('webSocketUrl')}")
            logger.info(f"_websocket_connection exists: {self.driver._websocket_connection is not None}")
            return False
        
        logger.info("BiDi basic availability check passed")
        logger.info(f"webSocketUrl: {self.driver.caps.get('webSocketUrl')}")
        logger.info(f"websocket_connection: {type(self.driver._websocket_connection)}")
        
        try:
            # Try a simple BiDi operation to test connectivity
            logger.info("Attempting browsing_context.get_tree() for health check...")
            result = self.driver.browsing_context.get_tree()
            logger.info(f"BiDi health check successful! Result: {result}")
            return True
        except Exception as e:
            logger.warning(f"BiDi health check failed with exception: {type(e).__name__}: {e}")
            import traceback
            logger.warning(f"Full traceback: {traceback.format_exc()}")
            return False

    def get_supported_commands(self) -> list[str]:
        """Get list of commands that can be executed with BiDi.
        
        Returns:
            List of supported command names.
        """
        return list(self.mapper.COMMAND_MAPPINGS.keys())

    def get_available_commands(self) -> list[str]:
        """Get list of commands that are currently available for BiDi execution.
        
        Returns:
            List of available command names (supported and not disabled).
        """
        return [
            cmd for cmd in self.mapper.COMMAND_MAPPINGS.keys()
            if cmd not in self._disabled_commands
        ]