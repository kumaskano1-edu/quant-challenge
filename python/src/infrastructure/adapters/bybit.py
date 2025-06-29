import aiohttp
import numpy as np

class BybitClient:
    """Клиент Bybit, чо. Тянем ордербук и считаем дельту."""

    BASE_URL = "https://api-testnet.bybit.com"

    def __init__(self) -> None:
        self._session = aiohttp.ClientSession()

    async def fetch_orderbook_snapshot(self, symbol: str, limit: int = 200) -> dict:
        """Асинхронно получаем срез ордербука."""
        url = f"{self.BASE_URL}/v5/market/orderbook"
        params = {"category": "linear", "symbol": symbol, "limit": limit}
        async with self._session.get(url, params=params) as resp:
            data = await resp.json()
            return data.get("result", {})

    async def calculate_delta(self, snapshot_prev: dict, snapshot_new: dict) -> float:
        """Высчитываем дельту между снапшотами."""
        bids_prev = np.array(snapshot_prev.get("b", []), dtype=float)
        asks_prev = np.array(snapshot_prev.get("a", []), dtype=float)
        bids_new = np.array(snapshot_new.get("b", []), dtype=float)
        asks_new = np.array(snapshot_new.get("a", []), dtype=float)

        delta_prev = bids_prev[:, 1].sum() - asks_prev[:, 1].sum() if bids_prev.size and asks_prev.size else 0.0
        delta_new = bids_new[:, 1].sum() - asks_new[:, 1].sum() if bids_new.size and asks_new.size else 0.0
        return float(delta_new - delta_prev)
    

    async def close(self) -> None:
        """Закрываем сессию aiohttp."""
        await self._session.close()
