"""Legacy entry point for FocusMate Mail AI.

This module preserves backward compatibility with earlier scripts by delegating
execution to the new modular `focusmate_app` CLI entry point.
"""

from focusmate_app import main


if __name__ == "__main__":
    main()
