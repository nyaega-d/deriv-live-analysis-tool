import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

class SignalScanner:
    """Advanced scanner for detecting accurate entry signals"""
    
    def __init__(self, min_accuracy: float = 90.0):
        self.min_accuracy = min_accuracy
        self.scan_history = defaultdict(list)
        self.signal_database = []
        self.pattern_memory = defaultdict(list)
        self.false_signals = []
        self.confirmed_signals = []
        
    def scan_for_signals(self, analyzer_data: Dict) -> List[Dict]:
        """Scan data for valid entry signals"""
        valid_signals = []
        
        matches = analyzer_data.get("matches_signal", {})
        differs = analyzer_data.get("differs_signal", {})
        
        # Check Matches signal
        if matches.get("signal") and matches.get("confidence", 0) >= self.min_accuracy:
            signal = self._create_signal_entry(
                pattern="MATCHES",
                data=matches,
                analyzer_data=analyzer_data
            )
            valid_signals.append(signal)
            self.signal_database.append(signal)
        
        # Check Differs signal
        if differs.get("signal") and differs.get("confidence", 0) >= self.min_accuracy:
            signal = self._create_signal_entry(
                pattern="DIFFERS",
                data=differs,
                analyzer_data=analyzer_data
            )
            valid_signals.append(signal)
            self.signal_database.append(signal)
        
        return valid_signals
    
    def _create_signal_entry(self, pattern: str, data: Dict, analyzer_data: Dict) -> Dict:
        """Create a complete signal entry"""
        timestamp = datetime.now()
        signal_id = f"{pattern}_{timestamp.timestamp()}"
        
        return {
            "id": signal_id,
            "pattern": pattern,
            "direction": data.get("signal"),
            "confidence": data.get("confidence", 0),
            "volatility": analyzer_data.get("current_volatility", 0),
            "atr": analyzer_data.get("atr", 0),
            "timestamp": timestamp.isoformat(),
            "status": "PENDING",
            "entry_price": None,
            "exit_price": None,
            "profit_loss": None
        }
    
    def validate_signal_accuracy(self, signal: Dict, price_history: List[float], 
                                expected_direction: str) -> Tuple[bool, float]:
        """Validate signal accuracy against price movement"""
        if len(price_history) < 2:
            return False, 0.0
        
        # Check if direction matches expected
        direction_correct = (signal["direction"] == expected_direction)
        
        # Calculate momentum strength
        price_moves = np.diff(price_history)
        momentum = np.mean(price_moves)
        
        # Calculate accuracy
        base_accuracy = signal["confidence"]
        momentum_bonus = min(20, abs(momentum) * 100)
        
        total_accuracy = min(100, base_accuracy + (momentum_bonus * 0.1))
        
        is_valid = (total_accuracy >= self.min_accuracy) and direction_correct
        
        return is_valid, total_accuracy
    
    def filter_signals_by_volatility(self, signals: List[Dict], 
                                     volatility_threshold: float = 0.02) -> List[Dict]:
        """Filter signals based on volatility conditions"""
        filtered = []
        
        for signal in signals:
            volatility = signal.get("volatility", 0)
            
            # Accept signals across all volatility ranges
            # But boost confidence in normal volatility
            if volatility < volatility_threshold:
                signal["volatility_condition"] = "LOW"
                signal["confidence"] *= 1.05  # 5% bonus
            elif volatility > volatility_threshold * 2:
                signal["volatility_condition"] = "HIGH"
                signal["confidence"] *= 0.95  # 5% penalty
            else:
                signal["volatility_condition"] = "NORMAL"
            
            # Ensure confidence doesn't exceed 100
            signal["confidence"] = min(100, signal["confidence"])
            
            if signal["confidence"] >= self.min_accuracy:
                filtered.append(signal)
        
        return filtered
    
    def confirm_signal(self, signal_id: str) -> bool:
        """Confirm a signal as valid"""
        for signal in self.signal_database:
            if signal["id"] == signal_id:
                signal["status"] = "CONFIRMED"
                self.confirmed_signals.append(signal)
                logger.info(f"Signal confirmed: {signal_id}")
                return True
        return False
    
    def mark_signal_false(self, signal_id: str, reason: str = ""):
        """Mark a signal as false positive"""
        for signal in self.signal_database:
            if signal["id"] == signal_id:
                signal["status"] = "FALSE"
                signal["false_reason"] = reason
                self.false_signals.append(signal)
                logger.warning(f"Signal marked false: {signal_id} - {reason}")
                return True
        return False
    
    def update_signal_result(self, signal_id: str, entry_price: float, 
                            exit_price: float):
        """Update signal with trade result"""
        for signal in self.signal_database:
            if signal["id"] == signal_id:
                signal["entry_price"] = entry_price
                signal["exit_price"] = exit_price
                signal["profit_loss"] = exit_price - entry_price
                signal["status"] = "COMPLETED"
                logger.info(f"Signal result updated: {signal_id} P/L: {signal['profit_loss']}")
                return signal
        return None
    
    def get_scanner_stats(self) -> Dict:
        """Get scanner statistics"""
        total_signals = len(self.signal_database)
        confirmed = len(self.confirmed_signals)
        false = len(self.false_signals)
        
        accuracy_rate = (confirmed / total_signals * 100) if total_signals > 0 else 0
        
        profitable_signals = sum(1 for s in self.confirmed_signals 
                                if s.get("profit_loss", 0) > 0)
        win_rate = (profitable_signals / confirmed * 100) if confirmed > 0 else 0
        
        total_pnl = sum(s.get("profit_loss", 0) for s in self.confirmed_signals)
        
        return {
            "total_signals": total_signals,
            "confirmed_signals": confirmed,
            "false_signals": false,
            "signal_accuracy": accuracy_rate,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "avg_confidence": np.mean([s["confidence"] for s in self.signal_database]) 
                             if self.signal_database else 0
        }
    
    def get_high_confidence_signals(self) -> List[Dict]:
        """Get only highest confidence signals (95%+)"""
        return [s for s in self.signal_database if s["confidence"] >= 95]
    
    def export_signals(self) -> List[Dict]:
        """Export all signals for review"""
        return self.signal_database.copy()
    
    def clear_old_signals(self, hours: int = 24):
        """Clear signals older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        original_count = len(self.signal_database)
        self.signal_database = [
            s for s in self.signal_database
            if datetime.fromisoformat(s["timestamp"]) > cutoff_time
        ]
        
        removed = original_count - len(self.signal_database)
        logger.info(f"Cleared {removed} old signals")
