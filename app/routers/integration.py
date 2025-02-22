from fastapi import APIRouter, BackgroundTasks, Request, status

from app.utils.monitor import HAProxyMonitor
from app.schema.monitor import MonitorPayload

router = APIRouter(prefix="", tags=["Hello World"])


@router.get("/integration.json")
async def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "date": {"created_at": "2025-02-20", "updated_at": "2025-02-20"},
            "descriptions": {
                "app_name": "HAProxy Stats Monitor",
                "app_description": "Monitors HAProxy statistics and sends daily reports to Telex.",
                "app_logo": "URL to the application logo.",
                "app_url": base_url,
                "background_color": "#4A90E2",
            },
            "integration_category": "Monitoring & Logging",
            "integration_type": "interval",
            "is_active": True,
            "output": [
                {
                    "label": "output_channel_1",
                    "value": True,
                },
            ],
            "key_features": [
                "Monitors HAProxy performance metrics.",
                "Sends regular stats updates to Telex.",
                "Configurable update interval.",
                "Supports customizable settings.",
            ],
            "permissions": {
                "monitoring_user": {
                    "always_online": True,
                    "display_name": "HAProxy Performance Monitor",
                },
            },
            "settings": [
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "* * * * *",  # "00:00",
                },
                {
                    "label": "Telex Webhook URL",
                    "type": "text",
                    "required": True,
                    "default": "https://telex.example.com/webhook",
                },
                {
                    "label": "HAProxy Admin Socket Path",
                    "type": "text",
                    "required": False,
                    "default": "/var/run/haproxy/admin.sock",
                },
            ],
            "tick_url": "http://example.com/tick_url",
        }
    }


@router.post("/tick", status_code=status.HTTP_202_ACCEPTED)
async def monitor_haproxy(payload: MonitorPayload, background_tasks: BackgroundTasks):
    monitor = HAProxyMonitor(payload.return_url)
    background_tasks.add_task(monitor.run_check)
    return {"status": "accepted"}
