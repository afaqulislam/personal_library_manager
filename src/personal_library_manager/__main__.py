"""Allow ``python -m personal_library_manager`` to launch the application."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
