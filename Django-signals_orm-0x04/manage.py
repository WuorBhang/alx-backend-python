#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys
from typing import NoReturn


def setup_logging() -> None:
    """Configure basic logging for the management script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_environment() -> None:
    """Validate that required environment variables and dependencies are available."""
    # Check if we're in a virtual environment (recommended practice)
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logging.warning("No virtual environment detected. Consider using a virtual environment.")
    
    # Validate Python version
    if sys.version_info < (3, 8):
        logging.error("Python 3.8 or higher is required for Django 4.x+")
        sys.exit(1)


def main() -> NoReturn:
    """
    Run administrative tasks with enhanced error handling and logging.
    
    This function sets up the Django environment and executes management commands
    with proper error handling, logging, and environment validation.
    
    Raises:
        ImportError: If Django is not properly installed or configured
        SystemExit: If critical environment requirements are not met
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate environment before proceeding
        validate_environment()
        
        # Set default Django settings module
        settings_module = "messaging_app.settings"
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        logger.info(f"Using Django settings module: {settings_module}")
        
        # Import Django management utilities
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            logger.error("Failed to import Django management utilities")
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        
        # Log the command being executed
        if len(sys.argv) > 1:
            logger.info(f"Executing Django management command: {' '.join(sys.argv[1:])}")
        
        # Execute the management command
        execute_from_command_line(sys.argv)
        
    except KeyboardInterrupt:
        logger.info("Management command interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except SystemExit as exc:
        # Re-raise SystemExit to maintain proper exit codes
        logger.info(f"Management command exited with code: {exc.code}")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error occurred: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
