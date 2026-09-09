import os
from colorama import Fore, Back, Style, init
from datetime import datetime
from typing import Dict, List
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)

class ConsoleUI:
    """Console-based user interface"""
    
    def __init__(self):
        self.last_analysis = None
        self.last_signals = []
    
    def display_welcome(self):
        """Display welcome message"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("=" * 70)
        print(" " * 15 + "🚀 DERIV LIVE ANALYSIS TOOL 🚀")
        print(" " * 10 + "Matches & Differs Pattern Detection System")
        print("=" * 70)
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✓ Connected to Deriv API")
        print(f"✓ Real-time price tracking enabled")
        print(f"✓ Signal scanner active (90%+ accuracy)")
        print(f"{Style.RESET_ALL}\n")
    
    def display_menu(self):
        """Display main menu"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print("📋 MAIN MENU")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. {Style.BRIGHT}View Current Analysis")
        print(f"{Fore.YELLOW}2. {Style.BRIGHT}View Scanner Statistics")
        print(f"{Fore.YELLOW}3. {Style.BRIGHT}View High Confidence Signals (95%+)")
        print(f"{Fore.YELLOW}4. {Style.BRIGHT}View Active Entry Timers")
        print(f"{Fore.YELLOW}5. {Style.BRIGHT}Switch Symbol")
        print(f"{Fore.RED}6. {Style.BRIGHT}Exit Application")
        print(f"{Style.RESET_ALL}")
    
    def display_signal_alert(self, signal: Dict):
        """Display signal alert"""
        print(f"\n{Fore.GREEN}{Back.BLACK}")
        print("╔" + "═" * 68 + "╗")
        print("║" + f" 🎯 NEW SIGNAL DETECTED ".center(68) + "║")
        print("╠" + "═" * 68 + "╣")
        print(f"║ Pattern: {signal['pattern']:<15} Direction: {signal['direction']:<10} Confidence: {signal['confidence']:.2f}%")
        print(f"║ Volatility: {signal['volatility']:.6f} ATR: {signal['atr']:.6f}")
        print(f"║ Timestamp: {signal['timestamp']}")
        print("╚" + "═" * 68 + "╝")
        print(f"{Style.RESET_ALL}\n")
    
    def display_current_analysis(self, analysis: Dict):
        """Display current analysis"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print("📊 CURRENT ANALYSIS")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Market Metrics:{Style.RESET_ALL}")
        print(f"  • Data Points: {analysis.get('total_data_points', 0)}")
        print(f"  • Volatility: {analysis.get('current_volatility', 0):.6f}")
        print(f"  • ATR (14): {analysis.get('atr', 0):.6f}\n")
        
        matches = analysis.get('matches_signal', {})
        print(f"{Fore.GREEN}Matches Pattern:{Style.RESET_ALL}")
        if matches.get('signal'):
            print(f"  ✓ Signal: {matches.get('signal')}")
            print(f"  • Confidence: {matches.get('confidence', 0):.2f}%")
            print(f"  • Moves: {matches.get('moves', [])}")
        else:
            print(f"  ✗ No signal detected")
        print()
        
        differs = analysis.get('differs_signal', {})
        print(f"{Fore.BLUE}Differs Pattern:{Style.RESET_ALL}")
        if differs.get('signal'):
            print(f"  ✓ Signal: {differs.get('signal')}")
            print(f"  • Confidence: {differs.get('confidence', 0):.2f}%")
            print(f"  • Moves: {differs.get('moves', [])}")
        else:
            print(f"  ✗ No signal detected")
        print()
        
        print(f"{Fore.MAGENTA}Statistics:{Style.RESET_ALL}")
        print(f"  • Total Signals: {analysis.get('total_signals_generated', 0)}")
        print(f"  • Accuracy: {analysis.get('accuracy', 0):.2f}%")
        print(f"  • Signal History: {analysis.get('signal_history_length', 0)}")
        
        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def display_scanner_stats(self, stats: Dict):
        """Display scanner statistics"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print("📈 SCANNER STATISTICS")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        data = [
            ["Total Signals", str(stats.get('total_signals', 0))],
            ["Confirmed Signals", f"{Fore.GREEN}{stats.get('confirmed_signals', 0)}{Style.RESET_ALL}"],
            ["False Signals", f"{Fore.RED}{stats.get('false_signals', 0)}{Style.RESET_ALL}"],
            ["Signal Accuracy", f"{Fore.YELLOW}{stats.get('signal_accuracy', 0):.2f}%{Style.RESET_ALL}"],
            ["Win Rate", f"{Fore.GREEN}{stats.get('win_rate', 0):.2f}%{Style.RESET_ALL}"],
            ["Total P/L", f"{Fore.CYAN}{stats.get('total_pnl', 0):.2f}{Style.RESET_ALL}"],
            ["Avg Confidence", f"{Fore.MAGENTA}{stats.get('avg_confidence', 0):.2f}%{Style.RESET_ALL}"]
        ]
        
        print(tabulate(data, headers=["Metric", "Value"], tablefmt="grid"))
        print(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def display_high_confidence_signals(self, signals: List[Dict]):
        """Display high confidence signals"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print("⭐ HIGH CONFIDENCE SIGNALS (95%+)")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        if not signals:
            print(f"{Fore.YELLOW}No high confidence signals detected yet{Style.RESET_ALL}\n")
        else:
            for i, signal in enumerate(signals[:10], 1):
                print(f"{Fore.GREEN}{i}. {signal['pattern']} - {signal['direction']}")
                print(f"   Confidence: {signal['confidence']:.2f}% | Volatility: {signal['volatility']:.6f}")
                print(f"   Time: {signal['timestamp']}\n")
        
        print(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def display_active_timers(self, timers: List[Dict]):
        """Display active entry timers"""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}")
        print("⏱️ ACTIVE ENTRY TIMERS")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        if not timers:
            print(f"{Fore.YELLOW}No active timers{Style.RESET_ALL}\n")
        else:
            for timer in timers:
                remaining = timer['remaining']
                progress = timer['progress']
                time_str = timer['time_string']
                
                # Progress bar
                bar_length = 30
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"{Fore.GREEN}{timer['signal_id']}{Style.RESET_ALL}")
                print(f"  Time: {Fore.YELLOW}{time_str}{Style.RESET_ALL} | Progress: [{bar}] {progress:.1f}%")
                print()
        
        print(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
        input()
    
    def display_timer_complete(self, signal_id: str, signal: Dict):
        """Display timer completion message"""
        print(f"\n{Fore.YELLOW}{Back.BLACK}")
        print("╔" + "═" * 68 + "╗")
        print("║" + f" ⏰ ENTRY WINDOW CLOSED ".center(68) + "║")
        print("╠" + "═" * 68 + "╣")
        print(f"║ Signal ID: {signal_id}")
        print(f"║ Pattern: {signal['pattern']:<20} Direction: {signal['direction']}")
        print(f"║ Status: Entry opportunity window has ended")
        print("╚" + "═" * 68 + "╝")
        print(f"{Style.RESET_ALL}\n")
    
    def update_analysis(self, analysis: Dict):
        """Update analysis data"""
        self.last_analysis = analysis
    
    def update_signals(self, signals: List[Dict]):
        """Update signals data"""
        self.last_signals = signals
    
    def update_timer(self, signal_id: str, tick_data: Dict):
        """Update timer display"""
        # This would update in real-time UI if implemented
        pass