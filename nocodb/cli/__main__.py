"""Entry point for running CLI as a module: python -m nocodb.cli"""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
