import sys
import traceback

try:
    from app import server as application
except Exception:
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
