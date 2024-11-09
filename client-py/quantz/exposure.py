from rich.live import Live
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from market import TradingClient, Side, Market
import time
from typing import Optional
from config import API_URL, JWT, ACT_AS

class MarketAnalyzer:
    def __init__(self):
        self.console = Console()
        self.client = TradingClient(API_URL, JWT, ACT_AS)
        self.current_market_id: Optional[int] = None
        self.simulation_price: Optional[float] = None
        
    def get_market_exposure(self, market_id: int):
        """Get our exposure to a specific market."""
        state = self.client.state()
        for exposure in state.portfolio.market_exposures:
            if exposure.market_id == market_id:
                return exposure
        return None
    
    def calculate_settlement_impact(self, market: Market, position: float, settle_price: float) -> float:
        """Calculate P&L if market settles at given price."""
        if hasattr(market, 'closed'):
            return 0  # Market already settled
        
        # Bound the settlement price
        settle_price = max(min(settle_price, market.max_settlement), market.min_settlement)
        
        # Simple P&L calculation: position * settlement_price
        # (This assumes the position was acquired at 0 cost - you'd need to track entry prices
        # for actual P&L calculation)
        return position * settle_price

    def generate_layout(self) -> Layout:
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="market_info"),
            Layout(name="settlement_analysis")
        )
        
        return layout

    def render_market_info(self, market: Market) -> Panel:
        """Render basic market information."""
        info = Text()
        info.append(f"Market ID: {market.id}\n", style="bold blue")
        info.append(f"Name: {market.name}\n", style="green")
        info.append(f"Description: {market.description}\n\n")
        info.append(f"Settlement Range: {market.min_settlement:.2f} to {market.max_settlement:.2f}\n")
        
        # Get our exposure
        exposure = self.get_market_exposure(market.id)
        if exposure:
            info.append("\nYour Position:\n", style="bold yellow")
            info.append(f"Net Position: {exposure.position:.2f}\n")
            info.append(f"Pending Buys: {exposure.total_bid_size:.2f} (${exposure.total_bid_value:.2f})\n")
            info.append(f"Pending Sells: {exposure.total_offer_size:.2f} (${exposure.total_offer_value:.2f})\n")
        
        return Panel(info, title="Market Information", border_style="blue")

    def render_settlement_analysis(self, market: Market) -> Panel:
        """Render settlement scenario analysis."""
        exposure = self.get_market_exposure(market.id)
        position = exposure.position if exposure else 0
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Settlement Price")
        table.add_column("P&L", justify="right")
        
        # Show several settlement scenarios
        range_size = market.max_settlement - market.min_settlement
        step = range_size / 10
        
        for price in [
            market.min_settlement,
            market.min_settlement + step * 2,
            market.min_settlement + step * 4,
            market.min_settlement + step * 6,
            market.min_settlement + step * 8,
            market.max_settlement
        ]:
            pnl = self.calculate_settlement_impact(market, position, price)
            style = "green" if pnl > 0 else "red" if pnl < 0 else "white"
            table.add_row(
                f"${price:.2f}",
                f"${pnl:.2f}",
                style=style
            )
        
        return Panel(table, title="Settlement Analysis", border_style="green")

    def run(self):
        """Main TUI loop."""
        state = self.client.state()
        
        # List available markets
        market_table = Table(show_header=True)
        market_table.add_column("ID")
        market_table.add_column("Name")
        
        for market_id, market in state.markets.items():
            market_table.add_row(str(market_id), market.name)
        
        self.console.print(market_table)
        self.console.print("Enter market ID to analyze (Ctrl+C to quit):")
        
        try:
            market_id = int(input("> "))
            market = state.markets.get(market_id)
            if not market:
                self.console.print("Market not found!")
                return
            
            self.current_market_id = market_id
            
            # Create live display
            layout = self.generate_layout()
            
            with Live(layout, refresh_per_second=1) as live:
                while True:
                    # Update state
                    state = self.client.state()
                    market = state.markets.get(market_id)
                    
                    # Update layout
                    layout["header"].update(
                        Panel(f"Analyzing Market {market_id} - Press Ctrl+C to exit")
                    )
                    layout["market_info"].update(self.render_market_info(market))
                    layout["settlement_analysis"].update(
                        self.render_settlement_analysis(market)
                    )
                    
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.console.print("\nExiting...")

if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    analyzer.run()