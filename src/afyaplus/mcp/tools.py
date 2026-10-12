"""MCP tool stubs with an external-call fallback (Week 7 reuse).

``execute`` always tries the configured MCP server first; when no
server is reachable (the normal case in automated tests and the demo)
it falls back to a deterministic stub response. The fallback reason is
carried on the result so callers and tests can see which path ran.
"""

from __future__ import annotations

import os
from typing import Any, Optional


class MCPTools:
    """Minimal MCP tool client that degrades to stub mode."""

    def __init__(self, mode: str = "auto") -> None:
        self.mode = mode
        self.call_count = 0

    # -- external boundary -------------------------------------------------
    def _call_external_service(self, tool: str, params: dict) -> Any:
        """Real MCP call. Never reached in stub mode / automated tests."""
        server_url = os.environ.get("AFYA_MCP_URL", "")
        if not server_url:
            raise RuntimeError("MCP server not configured (AFYA_MCP_URL unset)")
        raise RuntimeError(f"MCP transport unavailable for {tool} at {server_url}")

    # -- stub data ---------------------------------------------------------
    def _stub_data(self, tool: str, params: dict) -> dict:
        """Deterministic stub payloads keyed by tool name."""
        if tool == "find_clinic_by_county":
            county = str(params.get("county", "Nairobi"))
            clinics = [
                {"clinic_id": "KE-C-001", "name": "AfyaPlus Nairobi South", "county": county},
                {"clinic_id": "KE-C-002", "name": "AfyaPlus Nairobi East", "county": county},
            ]
            return {"county": county, "clinics": clinics, "source": "stub_catalog"}
        if tool == "plan_delivery_route":
            stops = list(params.get("stops", ["depot", "KE-C-001"]))
            return {
                "ordered_stops": stops,
                "estimated_minutes": 30 + 15 * max(len(stops) - 1, 0),
                "source": "stub_greedy_planner",
            }
        if tool == "list_catalog_items":
            return {"items": [], "source": "stub_catalog", "echo": dict(params)}
        return {"tool": tool, "echo": dict(params), "source": "stub_default"}

    # -- public API --------------------------------------------------------
    def execute(self, tool: str, params: Optional[dict] = None) -> dict:
        """Run a tool, falling back to the stub if the external call fails."""
        params = dict(params or {})
        self.call_count += 1
        try:
            data = self._call_external_service(tool, params)
            return {"status": "ok", "tool": tool, "data": data, "reason": "live_mcp"}
        except Exception as exc:  # noqa: BLE001 - deliberate fallback boundary
            data = self._stub_data(tool, params)
            return {
                "status": "stub",
                "tool": tool,
                "data": data,
                "reason": f"fallback to stub: {exc}",
            }
