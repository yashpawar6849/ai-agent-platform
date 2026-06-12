import sys
from pathlib import Path

# Ensure ai-agent-platform/ root is on path so top-level packages are importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
