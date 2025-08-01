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

import datetime
import json
import math
import pkgutil
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Union

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.bidi.common import command_builder

from .log import LogEntryAdded
from .session import Session


class LocalValue(ABC):
    """Base class for BiDi LocalValue types."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert to BiDi protocol dictionary format."""
        pass

    @classmethod
    def from_python(cls, value: Any) -> "LocalValue":
        """Convert a Python value to BiDi LocalValue type."""
        if isinstance(value, LocalValue):
            return value

        type_map = {
            type(None): lambda v: NullLocalValue(),
            bool: lambda v: BooleanLocalValue(v),
            str: lambda v: StringLocalValue(v),
            datetime.datetime: lambda v: DateLocalValue(v.isoformat() + ("Z" if v.tzinfo is None else "")),
            datetime.date: lambda v: DateLocalValue(
                datetime.datetime.combine(v, datetime.time.min).replace(tzinfo=datetime.timezone.utc).isoformat()
            ),
            list: lambda v: ArrayLocalValue([cls.from_python(item) for item in v]),
            tuple: lambda v: ArrayLocalValue([cls.from_python(item) for item in v]),
            set: lambda v: SetLocalValue([cls.from_python(item) for item in v]),
            dict: lambda v: ObjectLocalValue([[cls.from_python(k), cls.from_python(val)] for k, val in v.items()]),
        }

        # Handle int/float
        if isinstance(value, (int, float)):
            return NumberLocalValue.from_python_number(value)

        if isinstance(value, re.Pattern):
            return RegExpLocalValue(pattern=value.pattern, flags=_re_flags_to_js_flags(value.flags))

        # Use type_map for other types
        handler = type_map.get(type(value))
        if handler:
            return handler(value)

        raise TypeError(f"Cannot convert value of type {type(value).__name__} to BiDi LocalValue")


@dataclass
class RegExpLocalValue(LocalValue):
    pattern: str
    flags: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        value = {"pattern": self.pattern}
        if self.flags:
            value["flags"] = self.flags
        return {"type": "regexp", "value": value}


def _re_flags_to_js_flags(flags: int) -> str:
    js_flags = ""
    if flags & re.IGNORECASE:
        js_flags += "i"
    if flags & re.MULTILINE:
        js_flags += "m"
    if flags & re.DOTALL:
        js_flags += "s"
    if flags & re.UNICODE:
        js_flags += "u"
    return js_flags


@dataclass
class StringLocalValue(LocalValue):
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "string", "value": self.value}


@dataclass
class NumberLocalValue(LocalValue):
    value: Union[int, float, str]  # str for special numbers like "NaN", "Infinity"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "number", "value": self.value}

    @classmethod
    def from_python_number(cls, value: Union[int, float]) -> "LocalValue":
        """Create NumberLocalValue from Python number with special handling."""
        if isinstance(value, float):
            if math.isnan(value):
                return cls("NaN")
            elif math.isinf(value):
                return cls("Infinity" if value > 0 else "-Infinity")
            elif value == 0.0 and math.copysign(1.0, value) < 0:
                return cls("-0")

        # Handle BigInt case
        JS_MAX_SAFE_INTEGER = 9007199254740991
        if isinstance(value, int) and abs(value) > JS_MAX_SAFE_INTEGER:
            return BigIntLocalValue(str(value))

        return cls(value)


@dataclass
class BigIntLocalValue(LocalValue):
    value: str

    def to_dict(self) -> dict[str, Any]:
        return {"type": "bigint", "value": self.value}


@dataclass
class BooleanLocalValue(LocalValue):
    value: bool

    def to_dict(self) -> dict[str, Any]:
        return {"type": "boolean", "value": self.value}


class NullLocalValue(LocalValue):
    def to_dict(self) -> dict[str, Any]:
        return {"type": "null"}


class UndefinedLocalValue(LocalValue):
    def to_dict(self) -> dict[str, Any]:
        return {"type": "undefined"}


@dataclass
class DateLocalValue(LocalValue):
    value: str  # ISO 8601 format

    def to_dict(self) -> dict[str, Any]:
        return {"type": "date", "value": self.value}


@dataclass
class ArrayLocalValue(LocalValue):
    value: list[LocalValue]

    def to_dict(self) -> dict[str, Any]:
        return {"type": "array", "value": [item.to_dict() for item in self.value]}


@dataclass
class SetLocalValue(LocalValue):
    value: list[LocalValue]

    def to_dict(self) -> dict[str, Any]:
        return {"type": "set", "value": [item.to_dict() for item in self.value]}


@dataclass
class ObjectLocalValue(LocalValue):
    value: list[list[LocalValue]]  # list of key-value pairs

    def to_dict(self) -> dict[str, Any]:
        return {"type": "object", "value": [[k.to_dict(), v.to_dict()] for k, v in self.value]}


@dataclass
class ChannelLocalValue(LocalValue):
    channel: str
    ownership: str = "root"

    def to_dict(self) -> dict[str, Any]:
        return {"type": "channel", "value": {"channel": self.channel, "ownership": self.ownership}}


@dataclass
class RemoteValue:
    type: str
    value: Optional[Any] = None
    handle: Optional[str] = None
    internal_id: Optional[str] = None
    shared_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RemoteValue":
        """Create RemoteValue from BiDi protocol dictionary."""
        return cls(
            type=data.get("type", ""),
            value=data.get("value"),
            handle=data.get("handle"),
            internal_id=data.get("internalId"),
            shared_id=data.get("sharedId"),
        )

    def get_python_value(self) -> Any:
        """Extract Python value from RemoteValue."""
        if self.type == "string":
            return self.value
        elif self.type == "number":
            return self.value
        elif self.type == "boolean":
            return self.value
        elif self.type == "null":
            return None
        elif self.type == "undefined":
            return None
        else:
            return self.value


class _DomMutationHandler:
    """Class to handle DOM mutation functionality."""

    def __init__(self, conn, driver):
        self.conn = conn
        self.driver = driver
        self.script_message_subscribed = False
        self.dom_mutation_preload_id = None
        self.channel_name = "dom_mutation_channel"

    def add_handler(self, handler):
        """Adds a DOM mutation handler."""
        self._ensure_mutation_script_loaded()
        self._subscribe_to_script_messages()
        return self.conn.add_callback(ScriptMessage, self._create_message_handler(handler))

    def remove_handler(self, handler_id):
        """Removes a DOM mutation handler."""
        self.conn.remove_callback(ScriptMessage, handler_id)
        self._unsubscribe_from_script_messages()

    def _ensure_mutation_script_loaded(self):
        """Load the JavaScript mutation listener if not already loaded."""
        if self.dom_mutation_preload_id is not None:
            return

        # Load the JavaScript mutation listener
        _pkg = ".".join(__name__.split(".")[:-1])
        mutation_script = pkgutil.get_data(_pkg, "bidi-mutation-listener.js")
        if mutation_script is None:
            raise WebDriverException("Unable to find bidi-mutation-listener.js")

        script_text = mutation_script.decode("utf-8")

        # Create function declaration that sets up the mutation observer
        function_declaration = f"""
        (function(channel) {{
            {script_text}
            try {{
                observeMutations(channel);
            }} catch (e) {{
                console.error('Error setting up mutation observer:', e);
            }}
        }})
        """

        channel_argument = ChannelLocalValue(self.channel_name).to_dict()

        # Add preload script
        params = {"functionDeclaration": function_declaration, "arguments": [channel_argument]}
        result = self.conn.execute(command_builder("script.addPreloadScript", params))
        self.dom_mutation_preload_id = result["script"]

    def _subscribe_to_script_messages(self):
        if not self.script_message_subscribed:
            session = Session(self.conn)
            self.conn.execute(session.subscribe(ScriptMessage.event_class))
            self.script_message_subscribed = True

    def _unsubscribe_from_script_messages(self):
        if self.script_message_subscribed and ScriptMessage.event_class not in self.conn.callbacks:
            session = Session(self.conn)
            self.conn.execute(session.unsubscribe(ScriptMessage.event_class))
            self.script_message_subscribed = False

    def _create_message_handler(self, handler):
        def _handle_script_message(script_message):
            if script_message.channel != self.channel_name:
                return

            try:
                # Convert incoming data to RemoteValue
                remote_value = RemoteValue.from_dict(script_message.data)
                mutation_data = remote_value.get_python_value()

                # Handle both direct values and JSON strings
                if isinstance(mutation_data, str):
                    try:
                        mutation_data = json.loads(mutation_data)
                    except json.JSONDecodeError:
                        return

                # Create DOM mutation object and call handler
                mutation = self._create_dom_mutation(mutation_data)
                if mutation:
                    handler(mutation)

            except (json.JSONDecodeError, KeyError, AttributeError, TypeError):
                pass

        return _handle_script_message

    def _create_dom_mutation(self, mutation_data):
        if not isinstance(mutation_data, dict):
            return None

        element_id = mutation_data.get("target")
        if not element_id or not self.driver:
            return None

        try:
            from selenium.webdriver.common.by import By

            # Find element by the WebDriver ID attribute
            elements = self.driver.find_elements(By.CSS_SELECTOR, f"[data-__webdriver_id='{element_id}']")

            if not elements:
                return None

            return DomMutation(
                element=elements[0],
                attribute_name=mutation_data.get("name"),
                current_value=mutation_data.get("value"),
                old_value=mutation_data.get("oldValue"),
            )

        except Exception:
            return None


class ResultOwnership:
    """Represents the possible result ownership types."""

    NONE = "none"
    ROOT = "root"


class RealmType:
    """Represents the possible realm types."""

    WINDOW = "window"
    DEDICATED_WORKER = "dedicated-worker"
    SHARED_WORKER = "shared-worker"
    SERVICE_WORKER = "service-worker"
    WORKER = "worker"
    PAINT_WORKLET = "paint-worklet"
    AUDIO_WORKLET = "audio-worklet"
    WORKLET = "worklet"


@dataclass
class RealmInfo:
    """Represents information about a realm."""

    realm: str
    origin: str
    type: str
    context: Optional[str] = None
    sandbox: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "RealmInfo":
        """Creates a RealmInfo instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the realm information.

        Returns:
        -------
            RealmInfo: A new instance of RealmInfo.
        """
        if "realm" not in json:
            raise ValueError("Missing required field 'realm' in RealmInfo")
        if "origin" not in json:
            raise ValueError("Missing required field 'origin' in RealmInfo")
        if "type" not in json:
            raise ValueError("Missing required field 'type' in RealmInfo")

        return cls(
            realm=json["realm"],
            origin=json["origin"],
            type=json["type"],
            context=json.get("context"),
            sandbox=json.get("sandbox"),
        )


@dataclass
class Source:
    """Represents the source of a script message."""

    realm: str
    context: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "Source":
        """Creates a Source instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the source information.

        Returns:
        -------
            Source: A new instance of Source.
        """
        if "realm" not in json:
            raise ValueError("Missing required field 'realm' in Source")

        return cls(
            realm=json["realm"],
            context=json.get("context"),
        )


@dataclass
class EvaluateResult:
    """Represents the result of script evaluation."""

    type: str
    realm: str
    result: Optional[dict] = None
    exception_details: Optional[dict] = None

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "EvaluateResult":
        """Creates an EvaluateResult instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the evaluation result.

        Returns:
        -------
            EvaluateResult: A new instance of EvaluateResult.
        """
        if "realm" not in json:
            raise ValueError("Missing required field 'realm' in EvaluateResult")
        if "type" not in json:
            raise ValueError("Missing required field 'type' in EvaluateResult")

        return cls(
            type=json["type"],
            realm=json["realm"],
            result=json.get("result"),
            exception_details=json.get("exceptionDetails"),
        )


@dataclass
class DomMutation:
    """Represents a DOM mutation event."""

    element: Any  # WebElement reference
    attribute_name: str
    current_value: Optional[str]
    old_value: Optional[str]


class ScriptMessage:
    """Represents a script message event."""

    event_class = "script.message"

    def __init__(self, channel: str, data: dict, source: Source):
        self.channel = channel
        self.data = data
        self.source = source

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "ScriptMessage":
        """Creates a ScriptMessage instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the script message.

        Returns:
        -------
            ScriptMessage: A new instance of ScriptMessage.
        """
        if "channel" not in json:
            raise ValueError("Missing required field 'channel' in ScriptMessage")
        if "data" not in json:
            raise ValueError("Missing required field 'data' in ScriptMessage")
        if "source" not in json:
            raise ValueError("Missing required field 'source' in ScriptMessage")

        return cls(
            channel=json["channel"],
            data=json["data"],
            source=Source.from_json(json["source"]),
        )


class RealmCreated:
    """Represents a realm created event."""

    event_class = "script.realmCreated"

    def __init__(self, realm_info: RealmInfo):
        self.realm_info = realm_info

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "RealmCreated":
        """Creates a RealmCreated instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the realm created event.

        Returns:
        -------
            RealmCreated: A new instance of RealmCreated.
        """
        return cls(realm_info=RealmInfo.from_json(json))


class RealmDestroyed:
    """Represents a realm destroyed event."""

    event_class = "script.realmDestroyed"

    def __init__(self, realm: str):
        self.realm = realm

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> "RealmDestroyed":
        """Creates a RealmDestroyed instance from a dictionary.

        Parameters:
        -----------
            json: A dictionary containing the realm destroyed event.

        Returns:
        -------
            RealmDestroyed: A new instance of RealmDestroyed.
        """
        if "realm" not in json:
            raise ValueError("Missing required field 'realm' in RealmDestroyed")

        return cls(realm=json["realm"])


class Script:
    """BiDi implementation of the script module."""

    def __init__(self, conn, driver=None):
        self.conn = conn
        self.driver = driver
        self.log_entry_subscribed = False
        self._dom_mutation_handler = _DomMutationHandler(conn, driver)

    # High-level APIs for SCRIPT module

    def add_console_message_handler(self, handler):
        self._subscribe_to_log_entries()
        return self.conn.add_callback(LogEntryAdded, self._handle_log_entry("console", handler))

    def add_javascript_error_handler(self, handler):
        self._subscribe_to_log_entries()
        return self.conn.add_callback(LogEntryAdded, self._handle_log_entry("javascript", handler))

    def remove_console_message_handler(self, id):
        self.conn.remove_callback(LogEntryAdded, id)
        self._unsubscribe_from_log_entries()

    remove_javascript_error_handler = remove_console_message_handler

    def add_dom_mutation_handler(self, handler):
        """Adds a DOM mutation handler.

        Parameters:
        -----------
            handler: A function that will be called with DomMutation objects
                    when DOM mutations occur.

        Returns:
        -------
            int: The handler ID that can be used to remove the handler.
        """
        return self._dom_mutation_handler.add_handler(handler)

    def remove_dom_mutation_handler(self, handler_id):
        """Removes a DOM mutation handler.

        Parameters:
        -----------
            handler_id: The ID of the handler to remove.
        """
        self._dom_mutation_handler.remove_handler(handler_id)

    def pin(self, script: str) -> str:
        """Pins a script to the current browsing context.

        Parameters:
        -----------
            script: The script to pin.

        Returns:
        -------
            str: The ID of the pinned script.
        """
        return self._add_preload_script(script)

    def unpin(self, script_id: str) -> None:
        """Unpins a script from the current browsing context.

        Parameters:
        -----------
            script_id: The ID of the pinned script to unpin.
        """
        self._remove_preload_script(script_id)

    def execute(self, script: str, *args) -> dict:
        """Executes a script in the current browsing context.

        Parameters:
        -----------
            script: The script function to execute.
            *args: Arguments to pass to the script function.

        Returns:
        -------
            dict: The result value from the script execution.

        Raises:
        ------
            WebDriverException: If the script execution fails.
        """

        if self.driver is None:
            raise WebDriverException("Driver reference is required for script execution")
        browsing_context_id = self.driver.current_window_handle

        # Convert arguments to the format expected by BiDi call_function (LocalValue Type)
        arguments = []
        for arg in args:
            arguments.append(LocalValue.from_python(arg).to_dict())

        target = {"context": browsing_context_id}

        result = self._call_function(
            function_declaration=script, await_promise=True, target=target, arguments=arguments if arguments else None
        )

        if result.type == "success":
            return result.result
        else:
            error_message = "Error while executing script"
            if result.exception_details:
                if "text" in result.exception_details:
                    error_message += f": {result.exception_details['text']}"
                elif "message" in result.exception_details:
                    error_message += f": {result.exception_details['message']}"

            raise WebDriverException(error_message)

    # low-level APIs for script module
    def _add_preload_script(
        self,
        function_declaration: str,
        arguments: Optional[list[dict[str, Any]]] = None,
        contexts: Optional[list[str]] = None,
        user_contexts: Optional[list[str]] = None,
        sandbox: Optional[str] = None,
    ) -> str:
        """Adds a preload script.

        Parameters:
        -----------
            function_declaration: The function declaration to preload.
            arguments: The arguments to pass to the function.
            contexts: The browsing context IDs to apply the script to.
            user_contexts: The user context IDs to apply the script to.
            sandbox: The sandbox name to apply the script to.

        Returns:
        -------
            str: The preload script ID.

        Raises:
        ------
            ValueError: If both contexts and user_contexts are provided.
        """
        if contexts is not None and user_contexts is not None:
            raise ValueError("Cannot specify both contexts and user_contexts")

        params: dict[str, Any] = {"functionDeclaration": function_declaration}

        if arguments is not None:
            params["arguments"] = arguments
        if contexts is not None:
            params["contexts"] = contexts
        if user_contexts is not None:
            params["userContexts"] = user_contexts
        if sandbox is not None:
            params["sandbox"] = sandbox

        result = self.conn.execute(command_builder("script.addPreloadScript", params))
        return result["script"]

    def _remove_preload_script(self, script_id: str) -> None:
        """Removes a preload script.

        Parameters:
        -----------
            script_id: The preload script ID to remove.
        """
        params = {"script": script_id}
        self.conn.execute(command_builder("script.removePreloadScript", params))

    def _disown(self, handles: list[str], target: dict) -> None:
        """Disowns the given handles.

        Parameters:
        -----------
            handles: The handles to disown.
            target: The target realm or context.
        """
        params = {
            "handles": handles,
            "target": target,
        }
        self.conn.execute(command_builder("script.disown", params))

    def _call_function(
        self,
        function_declaration: str,
        await_promise: bool,
        target: dict,
        arguments: Optional[list[dict]] = None,
        result_ownership: Optional[str] = None,
        serialization_options: Optional[dict] = None,
        this: Optional[dict] = None,
        user_activation: bool = False,
    ) -> EvaluateResult:
        """Calls a provided function with given arguments in a given realm.

        Parameters:
        -----------
            function_declaration: The function declaration to call.
            await_promise: Whether to await promise resolution.
            target: The target realm or context.
            arguments: The arguments to pass to the function.
            result_ownership: The result ownership type.
            serialization_options: The serialization options.
            this: The 'this' value for the function call.
            user_activation: Whether to trigger user activation.

        Returns:
        -------
            EvaluateResult: The result of the function call.
        """
        params = {
            "functionDeclaration": function_declaration,
            "awaitPromise": await_promise,
            "target": target,
            "userActivation": user_activation,
        }

        if arguments is not None:
            params["arguments"] = arguments
        if result_ownership is not None:
            params["resultOwnership"] = result_ownership
        if serialization_options is not None:
            params["serializationOptions"] = serialization_options
        if this is not None:
            params["this"] = this

        result = self.conn.execute(command_builder("script.callFunction", params))
        return EvaluateResult.from_json(result)

    def _evaluate(
        self,
        expression: str,
        target: dict,
        await_promise: bool,
        result_ownership: Optional[str] = None,
        serialization_options: Optional[dict] = None,
        user_activation: bool = False,
    ) -> EvaluateResult:
        """Evaluates a provided script in a given realm.

        Parameters:
        -----------
            expression: The script expression to evaluate.
            target: The target realm or context.
            await_promise: Whether to await promise resolution.
            result_ownership: The result ownership type.
            serialization_options: The serialization options.
            user_activation: Whether to trigger user activation.

        Returns:
        -------
            EvaluateResult: The result of the script evaluation.
        """
        params = {
            "expression": expression,
            "target": target,
            "awaitPromise": await_promise,
            "userActivation": user_activation,
        }

        if result_ownership is not None:
            params["resultOwnership"] = result_ownership
        if serialization_options is not None:
            params["serializationOptions"] = serialization_options

        result = self.conn.execute(command_builder("script.evaluate", params))
        return EvaluateResult.from_json(result)

    def _get_realms(
        self,
        context: Optional[str] = None,
        type: Optional[str] = None,
    ) -> list[RealmInfo]:
        """Returns a list of all realms, optionally filtered.

        Parameters:
        -----------
            context: The browsing context ID to filter by.
            type: The realm type to filter by.

        Returns:
        -------
            List[RealmInfo]: A list of realm information.
        """
        params = {}

        if context is not None:
            params["context"] = context
        if type is not None:
            params["type"] = type

        result = self.conn.execute(command_builder("script.getRealms", params))
        return [RealmInfo.from_json(realm) for realm in result["realms"]]

    def _subscribe_to_log_entries(self):
        if not self.log_entry_subscribed:
            session = Session(self.conn)
            self.conn.execute(session.subscribe(LogEntryAdded.event_class))
            self.log_entry_subscribed = True

    def _unsubscribe_from_log_entries(self):
        if self.log_entry_subscribed and LogEntryAdded.event_class not in self.conn.callbacks:
            session = Session(self.conn)
            self.conn.execute(session.unsubscribe(LogEntryAdded.event_class))
            self.log_entry_subscribed = False

    def _handle_log_entry(self, type, handler):
        def _handle_log_entry(log_entry):
            if log_entry.type_ == type:
                handler(log_entry)

        return _handle_log_entry
