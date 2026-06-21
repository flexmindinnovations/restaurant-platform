import json
import os
from fastapi import APIRouter, Depends
from shared.api.response import ResponseEnvelope
from shared.api.security import require_roles
from typing import Any

router = APIRouter()
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "commission_rate": 10,
    "delivery_radius_km": 15,
    "min_order_value": 12.0,
    "base_delivery_fee": 3.5,
    "service_fee": 1.5,
    "ai_provider": "Gemini",
    "ai_api_key": "",
    "logo_url": "",
    "brand_name": "QuickBite",
}

def _load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_SETTINGS

def _save_settings(data):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

@router.get("", response_model=ResponseEnvelope[dict])
async def get_settings() -> ResponseEnvelope[dict]:
    return ResponseEnvelope(data=_load_settings())

@router.put("", response_model=ResponseEnvelope[dict])
async def save_settings(
    request: dict,
    _current_user: Any = Depends(require_roles("SUPER_ADMIN")),
) -> ResponseEnvelope[dict]:
    _save_settings(request)
    return ResponseEnvelope(data=_load_settings())
