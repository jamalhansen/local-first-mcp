import sys
from pathlib import Path

# Add src to sys.path to allow importing from the internal package
sys.path.append(str(Path(__file__).parent / "src"))

from local_first_mcp.server import main

if __name__ == "__main__":
    main()
