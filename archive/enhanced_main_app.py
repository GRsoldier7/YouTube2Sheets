"""
Enhanced Main App
Modern GUI application with enhanced error handling and logging
"""
import sys
import os
from pathlib import Path
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.enhanced_logging import get_logger, log_context, LogContext, performance_monitoring
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from src.services.async_integration import AsyncIntegration
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig
from config_loader import load_config

class EnhancedMainApp:
    """Enhanced main application with modern patterns."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.logger = get_logger("main_app")
        self.error_handler = EnhancedErrorHandler()
        
        # Load configuration
        self.config = load_config()
        
        # Initialize services
        self._initialize_services()
        
        # Setup GUI
        self._setup_gui()
        
        # Set logging context
        self.context = LogContext(
            service="MainApp",
            operation="application_startup",
            session_id=f"session_{datetime.now().timestamp()}"
        )
        
        with log_context(self.logger, self.context):
            self.logger.info("Enhanced main app initialized")
    
    def _initialize_services(self):
        """Initialize all services."""
        try:
            # YouTube service
            youtube_key = self.config.get('youtube_api_key')
            if youtube_key:
                self.youtube_config = YouTubeConfig(api_key=youtube_key)
                self.youtube_service = YouTubeService(self.youtube_config)
            else:
                self.logger.warning("YouTube API key not found")
                self.youtube_service = None
            
            # Sheets service
            service_account_file = self.config.get('google_sheets_service_account_json')
            spreadsheet_url = self.config.get('default_spreadsheet_url')
            
            if service_account_file and spreadsheet_url:
                import re
                sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
                if sheet_id_match:
                    sheet_id = sheet_id_match.group(1)
                    self.sheets_config = SheetsConfig(
                        service_account_file=service_account_file,
                        spreadsheet_id=sheet_id
                    )
                    self.sheets_service = SheetsService(self.sheets_config)
                else:
                    self.logger.warning("Invalid spreadsheet URL")
                    self.sheets_service = None
            else:
                self.logger.warning("Sheets configuration not found")
                self.sheets_service = None
            
            # Async integration
            if self.youtube_service and self.sheets_service:
                self.async_integration = AsyncIntegration(
                    self.youtube_config,
                    self.sheets_config
                )
            else:
                self.async_integration = None
                self.logger.warning("Async integration not available")
            
        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}")
            self.error_handler.handle_generic_error(e, ErrorContext(
                service="MainApp",
                operation="initialize_services",
                timestamp=datetime.now()
            ))
    
    def _setup_gui(self):
        """Setup the GUI."""
        self.root.title("YouTube2Sheets - Enhanced")
        self.root.geometry("1200x800")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create title
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="YouTube2Sheets - Enhanced",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Create status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Create start button
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Start Enhanced Sync",
            command=self._start_enhanced_sync,
            width=200,
            height=40
        )
        self.start_button.grid(row=2, column=0, pady=20)
        
        # Create log text area
        self.log_text = ctk.CTkTextbox(
            self.main_frame,
            width=800,
            height=400
        )
        self.log_text.grid(row=3, column=0, columnspan=2, pady=20, sticky="nsew")
        
        # Configure main frame grid
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
    
    def _start_enhanced_sync(self):
        """Start enhanced sync operation."""
        if not self.async_integration:
            self.logger.error("Async integration not available")
            self.status_label.configure(text="Error: Services not available")
            return
        
        # Update UI
        self.status_label.configure(text="Starting enhanced sync...")
        self.start_button.configure(state="disabled")
        
        # Run sync in thread
        def run_sync():
            try:
                with performance_monitoring(self.logger, "enhanced_sync") as monitor:
                    # Example channel IDs - replace with actual ones
                    channel_ids = ["UC_x5XG1OV2P6uZZ5FSM9Ttw"]
                    tab_name = "Enhanced_Test"
                    
                    results = self.async_integration.run_sync_with_async(
                        channel_ids=channel_ids,
                        tab_name=tab_name,
                        max_videos=10
                    )
                    
                    # Update UI on main thread
                    self.root.after(0, lambda: self._sync_completed(results))
                    
            except Exception as e:
                self.logger.error(f"Sync operation failed: {e}")
                self.root.after(0, lambda: self._sync_failed(str(e)))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
    
    def _sync_completed(self, results: Dict[str, Any]):
        """Handle sync completion."""
        self.status_label.configure(text="Sync completed")
        self.start_button.configure(state="normal")
        
        # Update log
        log_message = f"""
Sync Results:
- Success: {results['success']}
- Videos Processed: {results['videos_processed']}
- Videos Written: {results['videos_written']}
- Duration: {results['duration']:.2f}s
- Errors: {len(results.get('errors', []))}
"""
        self.log_text.insert("end", log_message)
        self.log_text.see("end")
        
        self.logger.info("Sync completed successfully", extra=results)
    
    def _sync_failed(self, error: str):
        """Handle sync failure."""
        self.status_label.configure(text="Sync failed")
        self.start_button.configure(state="normal")
        
        # Update log
        log_message = f"Sync failed: {error}\n"
        self.log_text.insert("end", log_message)
        self.log_text.see("end")
        
        self.logger.error(f"Sync failed: {error}")
    
    def run(self):
        """Run the application."""
        with log_context(self.logger, self.context):
            self.logger.info("Starting enhanced main app")
            self.root.mainloop()

def main():
    """Main entry point."""
    app = EnhancedMainApp()
    app.run()

if __name__ == "__main__":
    main()
