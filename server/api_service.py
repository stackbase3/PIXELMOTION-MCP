"""
PixelMotion REST & SSE API Service
Provides defined HTTP endpoints for the companion web application to interface
cleanly with the FastMCP server, rendering engine, and QA pipeline.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from pixelmotion.server.core.config import (
    BASE_DIR,
    DATA_DIR,
    PROJECTS_DIR,
    RENDERS_DIR
)
from pixelmotion.server.core.models import Project


def create_api_app(mcp_instance=None) -> FastAPI:
    app = FastAPI(
        title="PixelMotion MCP Backend",
        version="1.0.0",
        description="REST & SSE companion service for PixelMotion MCP"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if mcp_instance is None:
        from pixelmotion.server.mcp_server import mcp
        mcp_server = mcp
    else:
        mcp_server = mcp_instance

    # 1. MCP Protocol Endpoints
    @app.get("/api/mcp/tools")
    async def list_tools():
        return {"tools": mcp_server.list_tools()}

    @app.post("/api/mcp/call")
    async def call_tool_endpoint(payload: Dict[str, Any]):
        tool_name = payload.get("name")
        arguments = payload.get("arguments", {})
        res = await mcp_server.call_tool(tool_name, arguments)
        return res

    # 2. Project Management Endpoints
    @app.get("/api/projects")
    async def list_projects():
        projects = []
        if PROJECTS_DIR.exists():
            for p_dir in PROJECTS_DIR.iterdir():
                manifest = p_dir / "project.json"
                if manifest.exists():
                    try:
                        with open(manifest, "r") as f:
                            projects.append(json.load(f))
                    except Exception:
                        pass
        return {"projects": projects}

    @app.get("/api/projects/{project_id}")
    async def get_project(project_id: str):
        manifest = PROJECTS_DIR / project_id / "project.json"
        if not manifest.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        with open(manifest, "r") as f:
            return json.load(f)

    @app.post("/api/projects")
    async def create_project_endpoint(payload: Dict[str, Any]):
        proj_id = payload.get("project_id", f"proj_{int(time.time())}")
        name = payload.get("name", "Untitled Product Film")
        from pixelmotion.server.mcp_server import get_or_create_project
        proj = get_or_create_project(proj_id, name)
        return proj.dict()

    # 3. Direct Workflow Actions
    @app.post("/api/projects/{project_id}/plan")
    async def generate_plan_endpoint(project_id: str, payload: Dict[str, Any]):
        product_name = payload.get("product_name", "Trading Journal")
        feature_focus = payload.get("feature_focus", "Execution Analytics")
        duration_sec = payload.get("duration_seconds", 30)
        bpm = payload.get("bpm", 120.0)
        ref_id = payload.get("reference_id")

        res = await mcp_server.call_tool("motion_generate_plan", {
            "project_id": project_id,
            "product_name": product_name,
            "feature_focus": feature_focus,
            "duration_seconds": duration_sec,
            "bpm": bpm,
            "reference_id": ref_id
        })
        return res

    @app.post("/api/projects/{project_id}/render/preview")
    async def render_preview_endpoint(project_id: str, payload: Dict[str, Any]):
        scene_id = payload.get("scene_id")
        res = await mcp_server.call_tool("render_preview", {
            "project_id": project_id,
            "scene_id": scene_id
        })
        return res

    @app.get("/api/renders/{job_id}")
    async def get_render_job(job_id: str):
        res = await mcp_server.call_tool("render_status", {"job_id": job_id})
        return res

    # 4. Static Files for Companion Web Workspace
    companion_dir = BASE_DIR / "companion_app"
    if companion_dir.exists():
        app.mount("/companion", StaticFiles(directory=str(companion_dir), html=True), name="companion")

    # Static access to renders
    if RENDERS_DIR.exists():
        app.mount("/renders", StaticFiles(directory=str(RENDERS_DIR)), name="renders")

    @app.get("/")
    async def root():
        index_file = companion_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"status": "ok", "service": "PixelMotion MCP API"}

    return app
