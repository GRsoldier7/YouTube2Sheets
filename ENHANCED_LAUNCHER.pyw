"""
Enhanced Launcher
Modern launcher with comprehensive error handling and logging
"""
import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.environ['PYTHONPATH'] = str(project_root / "src")

def setup_logging():
    """Setup comprehensive logging."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"youtube2sheets_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("launcher")

def main():
    """Main entry point with enhanced error handling."""
    logger = setup_logging()
    
    try:
        logger.info("Starting YouTube2Sheets Enhanced Launcher")
        
        # Import and run enhanced main app
        from src.gui.enhanced_main_app import main as run_enhanced_app
        run_enhanced_app()
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements_enhanced.txt")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        
    finally:
        logger.info("Launcher finished")

if __name__ == "__main__":
    main()
