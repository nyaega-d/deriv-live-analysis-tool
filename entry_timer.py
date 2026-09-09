from datetime import datetime, timedelta
import logging
from typing import Optional, Callable
from threading import Timer
import time

logger = logging.getLogger(__name__)

class EntryTimer:
    """Manages entry countdown and timing for trade execution"""
    
    def __init__(self, duration_seconds: int = 60):
        self.duration_seconds = duration_seconds
        self.start_time = None
        self.end_time = None
        self.is_active = False
        self.timer = None
        self.on_tick_callback = None
        self.on_complete_callback = None
        self.current_second = 0
        
    def start(self, on_tick: Optional[Callable] = None, on_complete: Optional[Callable] = None):
        """Start the entry timer"""
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(seconds=self.duration_seconds)
        self.is_active = True
        self.current_second = 0
        self.on_tick_callback = on_tick
        self.on_complete_callback = on_complete
        
        logger.info(f"Entry timer started: {self.duration_seconds}s")
        self._tick()
    
    def _tick(self):
        """Internal timer tick"""
        if not self.is_active:
            return
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        remaining = self.duration_seconds - elapsed
        self.current_second = int(elapsed)
        
        if self.on_tick_callback:
            self.on_tick_callback({
                "elapsed": self.current_second,
                "remaining": max(0, int(remaining)),
                "percentage": (elapsed / self.duration_seconds) * 100
            })
        
        if remaining > 0:
            # Schedule next tick in 100ms
            self.timer = Timer(0.1, self._tick)
            self.timer.daemon = True
            self.timer.start()
        else:
            self.stop(completed=True)
    
    def stop(self, completed: bool = False):
        """Stop the timer"""
        self.is_active = False
        if self.timer:
            self.timer.cancel()
        
        if completed and self.on_complete_callback:
            self.on_complete_callback({
                "elapsed": self.duration_seconds,
                "remaining": 0,
                "status": "COMPLETED"
            })
            logger.info("Entry timer completed")
        else:
            logger.info("Entry timer stopped")
    
    def get_remaining(self) -> int:
        """Get remaining seconds"""
        if not self.is_active or not self.start_time:
            return self.duration_seconds
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        remaining = self.duration_seconds - elapsed
        return max(0, int(remaining))
    
    def get_progress_percentage(self) -> float:
        """Get timer progress as percentage"""
        if not self.start_time:
            return 0.0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        percentage = (elapsed / self.duration_seconds) * 100
        return min(100, max(0, percentage))
    
    def is_running(self) -> bool:
        """Check if timer is running"""
        return self.is_active
    
    def get_time_string(self) -> str:
        """Get formatted time string"""
        remaining = self.get_remaining()
        minutes = remaining // 60
        seconds = remaining % 60
        return f"{minutes:02d}:{seconds:02d}"


class MultiEntryTimer:
    """Manages multiple entry timers for different signals"""
    
    def __init__(self):
        self.timers = {}
        self.active_timers = []
    
    def create_timer(self, signal_id: str, duration: int = 60) -> EntryTimer:
        """Create a new entry timer"""
        timer = EntryTimer(duration)
        self.timers[signal_id] = timer
        self.active_timers.append(signal_id)
        logger.info(f"Created timer for signal: {signal_id}")
        return timer
    
    def start_timer(self, signal_id: str, on_tick: Optional[Callable] = None, 
                   on_complete: Optional[Callable] = None):
        """Start a specific timer"""
        if signal_id in self.timers:
            self.timers[signal_id].start(on_tick, on_complete)
            return True
        return False
    
    def stop_timer(self, signal_id: str, completed: bool = False):
        """Stop a specific timer"""
        if signal_id in self.timers:
            self.timers[signal_id].stop(completed)
            if signal_id in self.active_timers:
                self.active_timers.remove(signal_id)
            return True
        return False
    
    def get_timer_status(self, signal_id: str) -> Optional[dict]:
        """Get status of a specific timer"""
        if signal_id in self.timers:
            timer = self.timers[signal_id]
            return {
                "signal_id": signal_id,
                "remaining": timer.get_remaining(),
                "progress": timer.get_progress_percentage(),
                "is_running": timer.is_running(),
                "time_string": timer.get_time_string()
            }
        return None
    
    def get_all_active_timers(self) -> list:
        """Get all active timers"""
        return [self.get_timer_status(sid) for sid in self.active_timers]
    
    def stop_all(self):
        """Stop all active timers"""
        for signal_id in list(self.active_timers):
            self.stop_timer(signal_id)
        logger.info("All timers stopped")
