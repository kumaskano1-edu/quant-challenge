from typing import Literal, Optional
from datetime import datetime
import csv

OPEN_LONG_THRESHOLD = 0.02
CLOSE_LONG_THRESHOLD = 0.0
OPEN_SHORT_THRESHOLD = -0.02
CLOSE_SHORT_THRESHOLD = 0.0


class StrategySimulator:
    def __init__(self):
        self.position: Literal["flat", "long", "short"] = "flat"
        self.entry_price: Optional[float] = None
        self.pnl = 0.0
        self.trade_log = []

    def _mid_price(self, snapshot: dict) -> float:
        bids = snapshot.get("b", [])
        asks = snapshot.get("a", [])
        if not bids or not asks:
            return 0.0
        return (float(bids[0][0]) + float(asks[0][0])) / 2

    def update(self, delta: float, snapshot: dict):
        price = self._mid_price(snapshot)
        time = datetime.utcnow().isoformat()

        if self.position == "flat":
            if delta > OPEN_LONG_THRESHOLD:
                self.position = "long"
                self.entry_price = price
                self._log_trade(time, "OPEN LONG", price, delta)
            elif delta < OPEN_SHORT_THRESHOLD:
                self.position = "short"
                self.entry_price = price
                self._log_trade(time, "OPEN SHORT", price, delta)

        elif self.position == "long" and delta < CLOSE_LONG_THRESHOLD:
            profit = price - self.entry_price
            self.pnl += profit
            self._log_trade(time, "CLOSE LONG", price, delta, profit)
            self._reset()

        elif self.position == "short" and delta > CLOSE_SHORT_THRESHOLD:
            profit = self.entry_price - price
            self.pnl += profit
            self._log_trade(time, "CLOSE SHORT", price, delta, profit)
            self._reset()

    def _log_trade(self, time, action, price, delta, profit=None):
        entry = {
            "time": time,
            "action": action,
            "price": price,
            "delta": delta,
            "pnl": profit if profit is not None else ""
        }
        self.trade_log.append(entry)
        print(entry)


    def total_pnl(self, current_price: float) -> float:
        if self.position == "long" and self.entry_price is not None:
            return current_price - self.entry_price
        elif self.position == "short" and self.entry_price is not None:
            return self.entry_price - current_price
        return 0.0
    def _reset(self):
        self.position = "flat"
        self.entry_price = None

    def export_trades(self, filename="trades.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["time", "action", "price", "delta", "pnl"])
            writer.writeheader()
            writer.writerows(self.trade_log)
