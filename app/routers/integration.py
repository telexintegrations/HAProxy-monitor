from fastapi import APIRouter, BackgroundTasks, Request, status, HTTPException

from app.utils.monitor import HAProxyMonitor
from app.schema.monitor import MonitorPayload

router = APIRouter(prefix="", tags=["HAProxy Health and Performance Monitor"])


@router.get("/integration.json")
async def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "date": {"created_at": "2025-02-20", "updated_at": "2025-02-20"},
            "descriptions": {
                "app_name": "HAProxy Health and Performance Monitor",
                "app_description": "Monitors HAProxy statistics and sends daily reports to Telex.",
                "app_logo": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Haproxy-logo.png",
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
                    "default": "* * * * *",
                },
                {
                    "label": "stats_endpoint",
                    "type": "text",
                    "required": True,
                    "default": "http://ec2-13-60-212-132.eu-north-1.compute.amazonaws.com:9000/haproxy_stats;csv;",
                    "description": "HAProxy stats URL (e.g., http://haproxy:8404/stats;csv)",
                },
                {
                    "label": "username",
                    "type": "text",
                    "required": True,
                    "default": "",
                    "description": "Username for HAProxy stats authentication",
                },
                {
                    "label": "password",
                    "type": "text",
                    "required": True,
                    "default": "",
                    "description": "Password for HAProxy stats authentication",
                },
            ],
            "tick_url": "http://13.48.84.147:8000/tick",
            "target_url": "none",
        }
    }


@router.post("/tick", status_code=status.HTTP_202_ACCEPTED)
async def monitor_haproxy(payload: MonitorPayload, background_tasks: BackgroundTasks):
    # Initialize variables
    stats_endpoint = None
    username = None
    password = None

    # Extract settings based on labels
    for setting in payload.settings:
        if setting.label == "stats_endpoint":
            stats_endpoint = setting.default
        elif setting.label == "username":
            username = setting.default
        elif setting.label == "password":
            password = setting.default

    if not all([stats_endpoint, username, password]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required settings: stats_endpoint, username, or password",
        )

    print("stats_endpoint", stats_endpoint)

    monitor = HAProxyMonitor(
        telex_webhook_url=payload.return_url,
        stats_endpoint=stats_endpoint,
        username=username,
        password=password,
    )
    background_tasks.add_task(monitor.run_check)
    return {"status": "accepted"}
