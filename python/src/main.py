# main.py
import asyncio
from infrastructure import BybitClient
from application import StrategySimulator

async def main():
    client = BybitClient()
    print("ByBit Client Loaded")
    strategy = StrategySimulator()
    print("Strategy Loaded")
    
    try:
        symbol = "BTCUSDT"
        prev = await client.fetch_orderbook_snapshot(symbol)
        count = 0
        #BACKTESTING 100 TIMES
        while count < 100:
            await asyncio.sleep(2.5)
            #NEW ORDERBOOK FETCHED, DELTA CALCULATED
            new = await client.fetch_orderbook_snapshot(symbol)
            delta = await client.calculate_delta(prev, new)            
    
            strategy.update(delta, new)

            #PNL CALCULATED AFTER EACH TRADE        
            mid_price = strategy._mid_price(new)
            unrealized = strategy.total_pnl(mid_price)
            backtesting_pnl = strategy.pnl + unrealized
            count+=1
            prev = new

        #ONCE LOOP IS FINISHED, EXPORTING HAPPENS AND FINAL PNL IS PRINTED
        strategy.export_trades()
        print(f"Final PnL: {backtesting_pnl:.2f}")


    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught inside main")
        print("Stopping and exporting trades...")
        strategy.export_trades()
        print(f"Final PnL: {backtesting_pnl:.2f}")
    finally:
        await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught outside asyncio.run() - exiting program.")