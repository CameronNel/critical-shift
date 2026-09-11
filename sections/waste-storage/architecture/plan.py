"""Regenerate the current measured floorplan; never reset the connection contract."""
from pathlib import Path
exec(compile((Path(__file__).parent/'detailed_plan.py').read_text(),'detailed_plan.py','exec'))
