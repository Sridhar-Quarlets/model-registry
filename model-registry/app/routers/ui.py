from typing import Optional

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx


API_BASE = "http://localhost:8000"

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_token_from_session(request: Request) -> Optional[str]:
    token = request.session.get("access_token")
    return token


@router.get("/", response_class=HTMLResponse)
async def ui_home(request: Request, view: Optional[str] = None):
    # Landing page with split layout; shows login by default or register when view=register
    return templates.TemplateResponse("index.html", {"request": request, "view": view or "login"})


# Authentication
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/auth/token", data={"username": username, "password": password})
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            # Return to landing with error
            return templates.TemplateResponse("index.html", {"request": request, "view": "login", "error": "Invalid credentials"}, status_code=400)

        data = resp.json()
        request.session["access_token"] = data.get("access_token")
        return RedirectResponse(url="/ui/dashboard", status_code=303)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request, "error": None})


@router.post("/register")
async def register_action(request: Request, email: str = Form(...), password: str = Form(...)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{API_BASE}/auth/register", json={"email": email, "password": password})
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Avoid JSON parse if backend returned HTML/plain
            error_text = None
            if e.response is not None:
                try:
                    error_text = e.response.json().get("detail")
                except Exception:
                    error_text = e.response.text or "Registration failed"
            error = error_text or "Registration failed"
            return templates.TemplateResponse("index.html", {"request": request, "view": "register", "error": error}, status_code=400)

    # Auto-login after successful registration
    try:
        login_resp = await client.post(f"{API_BASE}/auth/token", data={"username": email, "password": password})
        login_resp.raise_for_status()
        token_data = login_resp.json()
        request.session["access_token"] = token_data.get("access_token")
        return RedirectResponse(url="/ui/dashboard", status_code=303)
    except Exception:
        return RedirectResponse(url="/ui/?view=login", status_code=303)


@router.post("/logout")
async def logout_action(request: Request):
    request.session.pop("access_token", None)
    return RedirectResponse(url="/ui/", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/?view=login", status_code=303)
    # Optionally fetch current user info to display on dashboard
    headers = {"Authorization": f"Bearer {token}"}
    current_user = None
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{API_BASE}/auth/me", headers=headers, timeout=5)
            if resp.status_code == 200:
                current_user = resp.json()
        except Exception:
            pass
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})


# Models
@router.get("/models", response_class=HTMLResponse)
async def models_list(request: Request, page: int = 1, size: int = 20):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)

    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/models/", params={"page": page, "size": size}, headers=headers)
        if resp.status_code == 401:
            return RedirectResponse(url="/ui/login", status_code=303)
        resp.raise_for_status()
        payload = resp.json()

    return templates.TemplateResponse("models/list.html", {"request": request, **payload})


@router.get("/models/new", response_class=HTMLResponse)
async def model_new(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    return templates.TemplateResponse("models/new.html", {"request": request, "error": None})


@router.post("/models/new")
async def model_create(
    request: Request,
    model_name: str = Form(...),
    display_name: str = Form(...),
    version: str = Form(...),
    model_type: str = Form(...),
    domain: str = Form(...),
    artifact_path: str = Form(...),
    model_format: str = Form(...),
    checksum: str = Form(...),
    tags: Optional[str] = Form(None),
):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "model_name": model_name,
        "display_name": display_name,
        "version": version,
        "model_type": model_type,
        "domain": domain,
        "artifact_path": artifact_path,
        "model_format": model_format,
        "checksum": checksum,
        "tags": tags,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_BASE}/models/register", json=payload, headers=headers)
        if resp.status_code == 401:
            return RedirectResponse(url="/ui/login", status_code=303)
        if resp.status_code >= 400:
            error = resp.json().get("detail", "Failed to create model")
            return templates.TemplateResponse("models/new.html", {"request": request, "error": error}, status_code=400)

    return RedirectResponse(url="/ui/models", status_code=303)


@router.get("/models/{model_id}", response_class=HTMLResponse)
async def model_detail(request: Request, model_id: str):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/models/{model_id}", headers=headers)
        if resp.status_code == 401:
            return RedirectResponse(url="/ui/login", status_code=303)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Model not found")
        resp.raise_for_status()
        model = resp.json()
    return templates.TemplateResponse("models/detail.html", {"request": request, "model": model})


@router.post("/models/{model_id}/delete")
async def model_delete(request: Request, model_id: str):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.delete(f"{API_BASE}/models/{model_id}", headers=headers)
        if resp.status_code == 401:
            return RedirectResponse(url="/ui/login", status_code=303)
    return RedirectResponse(url="/ui/models", status_code=303)


# Metrics
@router.get("/models/{model_id}/metrics", response_class=HTMLResponse)
async def model_metrics(request: Request, model_id: str):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/ui/login", status_code=303)
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_BASE}/metrics/{model_id}", headers=headers)
        if resp.status_code == 401:
            return RedirectResponse(url="/ui/login", status_code=303)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Model not found")
        resp.raise_for_status()
        data = resp.json()
    return templates.TemplateResponse("models/metrics.html", {"request": request, **data})


