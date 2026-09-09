import os
import sys
import logging
import time
from dotenv import load_dotenv
from threading import Thread
from datetime import datetime
from collections import deque

from deriv_api import DerivAPI
from signal_analyzer import SignalAnalyzer
from scanner import SignalScanner
from entry_timer import MultiEntryTimer
from ui_display import ConsoleUI

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deriv_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DerivLiveAnalyzer:
    """Main application orchestrator"""
    
    def __init__(self):
        self.api_key = os.getenv('DERIV_API_KEY')
        self.min_accuracy = float(os.getenv('MIN_ACCURACY_THRESHOLD', 90))
        self.scan_interval = float(os.getenv('SCAN_INTERVAL', 1))
        
        # Core components
        self.api = DerivAPI(self.api_key)
        self.analyzer = SignalAnalyzer()
        self.scanner = SignalScanner(self.min_accuracy)
        self.timers = MultiEntryTimer()
        self.ui = ConsoleUI()
        
        # Data tracking
        self.price_history = deque(maxlen=500)
        self.symbols = ["1HZ100V", "1HZ50V"]  # Plain index and 1s index
        self.current_symbol = self.symbols[0]
        self.is_running = False
        self.last_price = None
        
        # Symbol-specific analyzers
        self.symbol_analyzers = {
            symbol: SignalAnalyzer() for symbol in self.symbols
        }
        self.symbol_scanners = {
            symbol: SignalScanner(self.min_accuracy) for symbol in self.symbols
        }
    
    def start(self):
        """Start the live analysis tool"""
        try:
            logger.info("=" * 60)
            logger.info("DERIV LIVE ANALYSIS TOOL - STARTING")
            logger.info("=" * 60)
            
            # Connect to Deriv API
            if not self.api.connect():
                logger.error("Failed to connect to Deriv API")
                return False
            
            self.is_running = True
            
            # Setup callbacks
            self.api.callbacks['tick'] = self.on_tick_data
            self.api.callbacks['ohlc'] = self.on_ohlc_data
            
            # Start monitoring
            self._start_monitoring()
            
            # Display UI
            self.ui.display_welcome()
            self._run_interactive_mode()
            
            return True
            
        except Exception as e:
            logger.error(f"Critical error: {e}")
            return False
        finally:
            self.stop()
    
    def _start_monitoring(self):
        """Start background monitoring threads"""
        # Subscribe to tick data for plain index
        self.api.subscribe_ticks(self.symbols[0], self.on_tick_data)
        
        # Start analysis thread
        analysis_thread = Thread(target=self._analysis_loop, daemon=True)
        analysis_thread.start()
        
        logger.info("Monitoring started")
    
    def on_tick_data(self, data: dict):
        """Handle incoming tick data"""
        try:
            if 'tick' in data:
                tick = data['tick']
                price = tick.get('quote')
                timestamp = tick.get('epoch')
                
                if price and timestamp:
                    self.last_price = price
                    self.price_history.append(price)
                    
                    # Add to current symbol analyzer
                    self.analyzer.add_price(price, timestamp)
                    self.symbol_analyzers[self.current_symbol].add_price(price, timestamp)
                    
        except Exception as e:
            logger.error(f"Error processing tick data: {e}")
    
    def on_ohlc_data(self, data: dict):
        """Handle incoming OHLC data"""
        try:
            if 'ohlc' in data:
                ohlc = data['ohlc']
                # Process OHLC data if needed
                pass
        except Exception as e:
            logger.error(f"Error processing OHLC data: {e}")
    
    def _analysis_loop(self):
        """Main analysis loop"""
        while self.is_running:
            try:
                if len(self.price_history) >= 5:
                    # Perform analysis
                    analysis_data = self.analyzer.get_analysis_summary()
                    
                    # Scan for signals
                    signals = self.scanner.scan_for_signals(analysis_data)
                    
                    # Process new signals
                    for signal in signals:
                        self._process_signal(signal)
                    
                    # Update UI
                    self.ui.update_analysis(analysis_data)
                    self.ui.update_signals(self.scanner.signal_database)
                
                time.sleep(self.scan_interval)
                
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
    
    def _process_signal(self, signal: dict):
        """Process a new signal"""
        try:
            signal_id = signal['id']
            logger.info(f"NEW SIGNAL: {signal['pattern']} - {signal['direction']} - Confidence: {signal['confidence']:.2f}%")
            
            # Create and start entry timer
            timer = self.timers.create_timer(signal_id, duration=60)
            
            def on_timer_tick(tick_data):
                self.ui.update_timer(signal_id, tick_data)
            
            def on_timer_complete(complete_data):
                self.ui.display_timer_complete(signal_id, signal)
                logger.info(f"Entry window closed for signal: {signal_id}")
            
            self.timers.start_timer(signal_id, on_timer_tick, on_timer_complete)
            
            # Display alert
            self.ui.display_signal_alert(signal)
            
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
    
    def switch_symbol(self, symbol: str):
        """Switch between symbols"""
        if symbol in self.symbols:
            self.current_symbol = symbol
            self.analyzer = self.symbol_analyzers[symbol]
            logger.info(f"Switched to symbol: {symbol}")
            return True
        return False
    
    def get_current_analysis(self) -> dict:
        """Get current analysis summary"""
        if not self.analyzer:
            return {}
        return self.analyzer.get_analysis_summary()
    
    def get_scanner_stats(self) -> dict:
        """Get scanner statistics"""
        return self.scanner.get_scanner_stats()
    
    def get_high_confidence_signals(self) -> list:
        """Get high confidence signals (95%+)"""
        return self.scanner.get_high_confidence_signals()
    
    def validate_signal(self, signal_id: str, actual_direction: str):
        """Validate signal against actual movement"""
        for signal in self.scanner.signal_database:
            if signal['id'] == signal_id:
                if signal['direction'] == actual_direction:
                    self.scanner.confirm_signal(signal_id)
                    logger.info(f"Signal CONFIRMED: {signal_id}")
                else:
                    self.scanner.mark_signal_false(signal_id, "Direction mismatch")
                    logger.warning(f"Signal INVALIDATED: {signal_id}")
                return True
        return False
    
    def _run_interactive_mode(self):
        """Run interactive mode"""
        while self.is_running:
            try:
                self.ui.display_menu()
                choice = input("\n📊 Select option: ").strip()
                
                if choice == '1':
                    self.ui.display_current_analysis(self.get_current_analysis())
                elif choice == '2':
                    self.ui.display_scanner_stats(self.get_scanner_stats())
                elif choice == '3':
                    signals = self.get_high_confidence_signals()
                    self.ui.display_high_confidence_signals(signals)
                elif choice == '4':
                    self.ui.display_active_timers(self.timers.get_all_active_timers())
                elif choice == '5':
                    print("\nAvailable symbols:", ", ".join(self.symbols))
                    symbol = input("Enter symbol: ").strip().upper()
                    if self.switch_symbol(symbol):
                        print(f"✓ Switched to {symbol}")
                    else:
                        print(f"✗ Symbol not found")
                elif choice == '6':
                    self.is_running = False
                    print("\n⏹️ Shutting down...")
                    break
                else:
                    print("Invalid option")
                    
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Interactive mode error: {e}")
    
    def stop(self):
        """Stop the application"""
        logger.info("Stopping Deriv Live Analyzer...")
        self.is_running = False
        self.timers.stop_all()
        self.api.disconnect()
        logger.info("Application stopped")


def main():
    """Main entry point"""
    app = DerivLiveAnalyzer()
    app.start()


if __name__ == "__main__":
    main()