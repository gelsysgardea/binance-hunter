from typing import Literal, Tuple, Optional
from dataclasses import dataclass

import httpx
from core.binance.api import BinanceAPI

@dataclass
class ClaimResult:
    status: Literal["SUCCESS", "FAIL", "CAPTCHA", "EXPIRED", "RATE_LIMIT", "ALREADY_CLAIMED", "INVALID"]
    amount: float = 0.0
    currency: str = ""
    message: str = ""

class RedpacketHandler:
    async def handle_response(self, response_json: dict) -> ClaimResult:
        data = response_json.get("data", None)
        code = response_json.get("code", None)

        if response_json.get("success"):
            amount_str = response_json["data"]["grabAmountStr"]
            return ClaimResult(
                status="SUCCESS",
                amount=float(amount_str),
                currency=response_json["data"]["currency"],
                message=f"{amount_str} {response_json['data']['currency']}"
            )

        if data and "validateId" in data:
            return ClaimResult(status="CAPTCHA", message="¡MADRES! CAPTCHA detectado.")

        if code not in ["100002001", "403067", "403802", "403803", "PAY4001COM000"]:
            return ClaimResult(status="FAIL", message=f"Error inesperado: {response_json}")

        match code:
            case "100002001":
                return ClaimResult(status="EXPIRED", message="Sesión Expirada. ¡A renovar cookies!")
            case "403067":
                return ClaimResult(status="RATE_LIMIT", message="La chota de Binance nos trae en la mira.")
            case "403802":
                return ClaimResult(status="ALREADY_CLAIMED", message="Ya se acabó el pastel.")
            case "403803" | "PAY4001COM000":
                return ClaimResult(status="INVALID", message="Código más chafa que un billete de 3 pesos.")
        
        return ClaimResult(status="FAIL", message="Respuesta desconocida.")


    async def claim_code(self, code: str) -> ClaimResult:
        """Directly claims a code and returns a structured result."""
        response = await BinanceAPI.request_redpacket(code)
        if response is None:
            return ClaimResult(status="FAIL", message="Fallo en la petición HTTP.")
        
        return await self.handle_response(response.json())
