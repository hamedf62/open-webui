import json
import logging

import requests
from open_webui.config import WEBUI_FAVICON_URL, WEBUI_NAME
from open_webui.env import SRC_LOG_LEVELS, VERSION, WEBHOOK_TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["WEBHOOK"])


def post_webhook(url: str, message: str, event_data: dict) -> bool:
    try:
        payload = {}

        # Slack and Google Chat Webhooks
        if "https://hooks.slack.com" in url or "https://chat.googleapis.com" in url:
            payload["text"] = message
        # Discord Webhooks
        elif "https://discord.com/api/webhooks" in url:
            payload["content"] = message
        # Microsoft Teams Webhooks
        elif "webhook.office.com" in url:
            action = event_data.get("action", "undefined")
            facts = [
                {"name": name, "value": value}
                for name, value in json.loads(event_data.get("user", {})).items()
            ]
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": message,
                "sections": [
                    {
                        "activityTitle": message,
                        "activitySubtitle": f"{WEBUI_NAME} ({VERSION}) - {action}",
                        "activityImage": WEBUI_FAVICON_URL,
                        "facts": facts,
                        "markdown": True,
                    }
                ],
            }
        # Telegram Bot
        elif "https://api.telegram.org/bot" in url:
            # payload["content"] = message
            payload = {
                    'chat_id': WEBHOOK_TELEGRAM_CHAT_ID,
                    'text': message
                }
        # Default Payload
        else:
            payload = {**event_data}

        log.debug(f"payload: {payload}")
        r = requests.post(url, json=payload)
        r.raise_for_status()
        log.debug(f"r.text: {r.text}")
        return True
    except Exception as e:
        log.exception(e)
        return False
