from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from time import sleep
from typing import Dict, Optional
from dataclasses import dataclass
from websockets.sync.client import ClientConnection, connect
import betterproto
import logging
from market import (
    TradingClient, 
    Side, 
    Market, 
    Portfolio,
    State
)
from config import API_URL, JWT, ACT_AS, config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardClient:
    """Wrapper for TradingClient that maintains connection and market mappings."""
    
    def __init__(self, api_url: str, jwt: str, act_as: str):
        self.client = TradingClient(api_url, jwt, act_as)
        # Map of market IDs to readable names
        self.market_names = {
            3: "high",
            4: "low",
            5: "sum"
        }
    
    def get_markets(self) -> Dict[str, Optional[Market]]:
        """Get current state of all markets with human-readable names."""
        state = self.client.state()
        return {
            name: state.markets.get(id)
            for id, name in self.market_names.items()
        }
    
    def get_portfolio(self) -> Portfolio:
        """Get current portfolio state."""
        return self.client.state().portfolio

class Dashboard:
    """Terminal UI dashboard for market data visualization."""
    
    def __init__(self):
        self.console = Console()

    def create_market_table(self, market: Market, name: str) -> Table:
        """Create a rich table showing market order book."""
        table = Table(title=f"Market: {name.upper()}", box=box.ROUNDED)
        
        # Order book columns
        table.add_column("Side", style="bold")
        table.add_column("Price", justify="right", style="cyan")
        table.add_column("Size", justify="right")
        table.add_column("Total Value", justify="right")
        
        # Sort and group orders by side
        bids = [o for o in market.orders if o.side == Side.BID]
        offers = [o for o in market.orders if o.side == Side.OFFER]
        
        # Sort bids descending, offers ascending
        bids.sort(key=lambda x: x.price, reverse=True)
        offers.sort(key=lambda x: x.price)
        
        # Add offers (sells) in red
        for order in offers[:5]:  # Top 5 offers
            total = order.price * order.size
            table.add_row(
                "SELL",
                f"{order.price:.2f}",
                f"{order.size:.2f}",
                f"{total:.2f}",
                style="red"
            )
        
        # Spread row
        if bids and offers:
            spread = offers[0].price - bids[0].price
            table.add_row("SPREAD", f"{spread:.2f}", "", "", style="yellow bold")
        
        # Add bids (buys) in green
        for order in bids[:5]:  # Top 5 bids
            total = order.price * order.size
            table.add_row(
                "BUY",
                f"{order.price:.2f}",
                f"{order.size:.2f}",
                f"{total:.2f}",
                style="green"
            )
        
        return table

    def create_trades_table(self, market: Market) -> Table:
        """Create a rich table showing recent trades."""
        table = Table(title="Recent Trades", box=box.ROUNDED)
        table.add_column("Price", justify="right", style="cyan")
        table.add_column("Size", justify="right")
        table.add_column("Total Value", justify="right")
        
        for trade in market.trades[-5:]:  # Last 5 trades
            total = trade.price * trade.size
            table.add_row(
                f"{trade.price:.2f}",
                f"{trade.size:.2f}",
                f"{total:.2f}"
            )
        
        return table

    def create_portfolio_panel(self, portfolio: Portfolio) -> Panel:
        """Create a panel showing portfolio information."""
        text = Text()
        text.append(f"💰 Total Balance: {portfolio.total_balance:.2f}\n", style="green")
        text.append(f"💵 Available Balance: {portfolio.available_balance:.2f}\n", style="blue")
        
        # Add market exposures
        if portfolio.market_exposures:
            text.append("\nMarket Exposures:\n", style="bold")
            for exposure in portfolio.market_exposures:
                text.append(f"Market {exposure.market_id}: {exposure.position:.2f}\n")
        
        return Panel(text, title="Portfolio", box=box.ROUNDED)

    def display(self, markets: Dict[str, Market], portfolio: Portfolio):
        """Display the main dashboard."""
        self.console.clear()
        
        # Show portfolio information
        self.console.print(self.create_portfolio_panel(portfolio))
        
        # Display each market
        for name, market in markets.items():
            if market:
                self.console.print(self.create_market_table(market, name))
                self.console.print(self.create_trades_table(market))
                self.console.print()

def main():
    # These would typically come from environment variables or config file
    API_URL = "wss://trading-bootcamp.fly.dev/api"
    

    try:
        client = DashboardClient(API_URL, JWT, ACT_AS)
        dashboard = Dashboard()
        
        while True:
            try:
                markets = client.get_markets()
                portfolio = client.get_portfolio()
                dashboard.display(markets, portfolio)
                sleep(1)  # Update frequency
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
                sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Shutting down dashboard...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()