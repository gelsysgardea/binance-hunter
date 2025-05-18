import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

def _parse_chat_ids(raw: str) -> List[int]:
    if not raw:
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip()]

@dataclass
class BaseConfig:
    # Telegram user session
    API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
    API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    CLIENT_NAME: str = os.getenv("TELEGRAM_CLIENT_NAME", "UserSession")

    # Optional Telegram control bot
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("TELEGRAM_ADMIN_ID", "0") or 0)

    @property
    def CHATS(self) -> List[int]:
        return _parse_chat_ids(os.getenv("TELEGRAM_CHAT_IDS", ""))

    @property
    def HEADERS(self) -> Dict[str, str]:
        return {
            "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0"),
            "bnc-uuid": os.getenv("BNC_UUID", ""),
            "device-info": os.getenv("DEVICE_INFO", ""),
            "clienttype": "web",
            "csrftoken": os.getenv("CSRF_TOKEN", ""),
            "fvideo-id": os.getenv("FVIDEO_ID", ""),
            "lang": os.getenv("BINANCE_LANG", "es-MX"),
            "Referer": os.getenv(
                "BINANCE_REFERER",
                "https://www.binance.com/es-MX/my/wallet/account/payment/cryptobox",
            ),
            "Cookie": os.getenv("BINANCE_COOKIE", ""),
        }

config = BaseConfig()
