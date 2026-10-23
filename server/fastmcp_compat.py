"""
FastMCP Compatible Protocol Implementation for PixelMotion
Provides genuine Model Context Protocol (MCP) server support with:
- JSON-RPC 2.0 message handling
- Automatic schema generation from Python type hints and docstrings
- Stdio transport for standard MCP clients (Claude Desktop, Cursor, Zed)
- SSE/HTTP transport for web & remote clients
- Full tools/list, tools/call, and initialize capabilities.
"""

import sys
import json
import inspect
import asyncio
import traceback
from typing import Callable, Dict, Any, List, Optional, get_type_hints


def python_type_to_json_schema(py_type) -> Dict[str, Any]:
    """Convert python type hint to JSON schema snippet."""
    if py_type == str:
        return {"type": "string"}
    elif py_type == int:
        return {"type": "integer"}
    elif py_type == float:
        return {"type": "number"}
    elif py_type == bool:
        return {"type": "boolean"}
    elif py_type in (list, List) or getattr(py_type, "__origin__", None) in (list, List):
        return {"type": "array"}
    elif py_type in (dict, Dict) or getattr(py_type, "__origin__", None) in (dict, Dict):
        return {"type": "object"}
    elif hasattr(py_type, "schema") and callable(getattr(py_type, "schema")):
        # Pydantic v1 model
        return py_type.schema()
    elif hasattr(py_type, "model_json_schema") and callable(getattr(py_type, "model_json_schema")):
        # Pydantic v2 model
        return py_type.model_json_schema()
    return {"type": "string"}


class FastMCPTool:
    def __init__(self, fn: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.fn = fn
        self.name = name or fn.__name__
        self.description = description or (fn.__doc__.strip() if fn.__doc__ else f"Tool {self.name}")
        self.schema = self._build_input_schema()

    def _build_input_schema(self) -> Dict[str, Any]:
        sig = inspect.signature(self.fn)
        type_hints = {}
        try:
            type_hints = get_type_hints(self.fn)
        except Exception:
            pass

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            py_type = type_hints.get(param_name, str)
            prop = python_type_to_json_schema(py_type)
            prop["description"] = f"Parameter {param_name}"
            properties[param_name] = prop

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    async def execute(self, arguments: Dict[str, Any]) -> Any:
        sig = inspect.signature(self.fn)
        bound = sig.bind_partial(**arguments)
        bound.apply_defaults()
        if asyncio.iscoroutinefunction(self.fn):
            return await self.fn(*bound.args, **bound.kwargs)
        else:
            return self.fn(*bound.args, **bound.kwargs)


class FastMCP:
    """
    FastMCP server implementation matching Model Context Protocol 2024-11-05 spec.
    """
    def __init__(self, name: str = "pixelmotion", version: str = "1.0.0", description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.tools: Dict[str, FastMCPTool] = {}
        self.prompts: Dict[str, Any] = {}
        self.resources: Dict[str, Any] = {}

    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        """Decorator to register a tool function."""
        def decorator(fn: Callable):
            tool_name = name or fn.__name__
            t = FastMCPTool(fn, name=tool_name, description=description)
            self.tools[tool_name] = t
            return fn
        return decorator

    def add_tool(self, fn: Callable, name: Optional[str] = None, description: Optional[str] = None):
        tool_name = name or fn.__name__
        self.tools[tool_name] = FastMCPTool(fn, name=tool_name, description=description)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.schema
            }
            for t in self.tools.values()
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.tools:
            return {
                "content": [{"type": "text", "text": f"Error: Tool '{name}' not found."}],
                "isError": True
            }
        try:
            result = await self.tools[name].execute(arguments)
            if isinstance(result, (dict, list)):
                text_result = json.dumps(result, indent=2)
            else:
                text_result = str(result)
            return {
                "content": [{"type": "text", "text": text_result}],
                "isError": False
            }
        except Exception as e:
            err_trace = traceback.format_exc()
            return {
                "content": [{"type": "text", "text": f"Execution error in {name}: {str(e)}\n{err_trace}"}],
                "isError": True
            }

    async def handle_jsonrpc_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes a single JSON-RPC 2.0 message."""
        msg_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": self.name,
                        "version": self.version
                    },
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False}
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": self.list_tools()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            call_res = await self.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": call_res
            }

        elif method == "resources/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"resources": []}}

        elif method == "prompts/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"prompts": []}}

        else:
            if msg_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found."
                    }
                }
            return None

    def run_stdio(self):
        """Run stdio JSON-RPC loop synchronously."""
        asyncio.run(self._run_stdio_async())

    async def _run_stdio_async(self):
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

        while True:
            line = await reader.readline()
            if not line:
                break
            raw_str = line.decode("utf-8").strip()
            if not raw_str:
                continue
            try:
                msg = json.loads(raw_str)
                response = await self.handle_jsonrpc_message(msg)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000):
        if transport == "stdio":
            self.run_stdio()
        elif transport in ("sse", "http"):
            from pixelmotion.server.api_service import create_api_app
            import uvicorn
            app = create_api_app(self)
            uvicorn.run(app, host=host, port=port)
        else:
            raise ValueError(f"Unknown transport: {transport}")
