import httpx
from core.config import config
from typing import Optional

class BinanceAPI:
    def __init__(self) -> None: ...

    @staticmethod
    async def request_redpacket(redpacket_code: str) -> Optional[httpx.Response]:
        """
        Send request to Binance API.
        This is a static method as it does not depend on class instance state.
        """
        async with httpx.AsyncClient(headers=config.HEADERS) as client:
            try:
                response = await client.post(
                    "https://www.binance.com/bapi/pay/v1/private/binance-pay/gift-box/code/grabV2",
                    json={
                        "channel": "DEFAULT",
                        "grabCode": redpacket_code,
                        "scene": None,
                    },
                )
                return response
            except BaseException as error:
                print(
                    f"An unexpected error occurred while processing the POST request to Binance API:\n{error=}"
                )
                return None
