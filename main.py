import httpx
import os
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, SecretStr, TypeAdapter

load_dotenv()

mcp = FastMCP("monobank")


class Settings(BaseModel):
    API_TOKEN: SecretStr = Field(
        default="X_TOKEN_PLACEHOLDER",
        description="Monobank API token",
    )


settings = Settings(API_TOKEN=os.getenv("MONOBANK_API_TOKEN", "X_TOKEN_PLACEHOLDER"))


class Account(BaseModel):
    id: str
    send_id: str = Field(alias="sendId")
    balance: int
    credit_limit: int = Field(alias="creditLimit")
    type: str
    currency_code: int = Field(alias="currencyCode")
    cashback_type: str = Field(alias="cashbackType")
    masked_pan: List[str] = Field(alias="maskedPan")
    iban: str


class Jar(BaseModel):
    id: str
    send_id: str = Field(alias="sendId")
    title: str
    description: Optional[str] = None
    currency_code: int = Field(alias="currencyCode")
    balance: int
    goal: Optional[int] = None


class ClientInfo(BaseModel):
    client_id: str = Field(alias="clientId")
    name: str
    webhook_url: str = Field(alias="webHookUrl")
    permissions: str
    accounts: List[Account]
    jars: Optional[List[Jar]] = None


class StatementItem(BaseModel):
    id: str
    time: int
    description: str
    mcc: int
    original_mcc: int = Field(alias="originalMcc")
    hold: bool
    amount: int
    operation_amount: int = Field(alias="operationAmount")
    currency_code: int = Field(alias="currencyCode")
    commission_rate: int = Field(alias="commissionRate")
    cashback_amount: int = Field(alias="cashbackAmount")
    balance: int
    comment: Optional[str] = Field(default=None)
    receipt_id: Optional[str] = Field(alias="receiptId", default=None)
    invoice_id: Optional[str] = Field(alias="invoiceId", default=None)
    counter_edrpou: Optional[str] = Field(alias="counterEdrpou", default=None)
    counter_iban: Optional[str] = Field(alias="counterIban", default=None)
    counter_name: Optional[str] = Field(alias="counterName", default=None)


@mcp.tool()
async def get_client_info() -> dict:
    """
    Get client information from Monobank API.

    This tool retrieves information about the client, their accounts, and jars.
    It requires a Monobank API token with the necessary permissions.
    """
    api_url = "https://api.monobank.ua/personal/client-info"
    headers = {"X-Token": settings.API_TOKEN.get_secret_value()}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
    except httpx.RequestError as e:
        raise ConnectionError(f"Failed to connect to Monobank API: {e}") from e

    return ClientInfo.model_validate(response.json()).model_dump()


@mcp.tool()
async def get_statement(
    account_id: str, from_timestamp: int, to_timestamp: int
) -> List[dict]:
    """
    Get account statement for a given period.
    Rate limit: 1 request per 60 seconds.
    Max period: 31 days + 1 hour.

    Rules: 
    1. Fetch from default account (account_id = "0") unless user specified another account explicitly.
    2. The amount of money is displayed in the smallest currency unit (kopiyka for UAH, cent for USD etc.). Convert to UAH/USD etc. accordingly, do not give user amounts in kopiyka.
    
    Parameters:
        account_id: Account identifier from the list of accounts, or "0" for the default account.
        from_timestamp: Start of the statement period (Unix timestamp).
        to_timestamp: End of the statement period (Unix timestamp).
    """
    to_timestamp = to_timestamp or int(datetime.now().timestamp())

    api_url = (
        f"https://api.monobank.ua/personal/statement/{account_id}/"
        f"{from_timestamp}/{to_timestamp}"
    )
    headers = {"X-Token": settings.API_TOKEN.get_secret_value()}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
    except httpx.RequestError as e:
        raise ConnectionError(f"Failed to connect to Monobank API: {e}") from e

    statement_item_list_validator = TypeAdapter(List[StatementItem])
    validated_items = statement_item_list_validator.validate_python(response.json())

    return [item.model_dump() for item in validated_items]


if __name__ == "__main__":
    mcp.run(transport="stdio")


