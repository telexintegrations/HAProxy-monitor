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
                "app_logo": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fen.m.wikipedia.org%2Fwiki%2FFile%3AHaproxy-logo.png&psig=AOvVaw3VtXG48vq-Qp_uoGvf4t8f&ust=1740314516621000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCMCC7PWm14sDFQAAAAAdAAAAABAE",
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
            "tick_url": "http://http://13.48.84.147:8000/tick",
            "target_url": "none",
        }
    }


@router.post("/tick", status_code=status.HTTP_202_ACCEPTED)
async def monitor_haproxy(payload: MonitorPayload, background_tasks: BackgroundTasks):
    monitor = HAProxyMonitor(payload.return_url)
    background_tasks.add_task(monitor.run_check)
    return {"status": "accepted"}
