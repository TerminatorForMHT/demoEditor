import os
import sys
from pathlib import Path

ENCODE = 'utf-8'
SEP = '\\' if sys.platform == "win32" else '/'
ROOT_PATH = Path(os.path.abspath(__file__)).parent.parent
IMG_PATH = ROOT_PATH / 'src' / 'static' / 'img'
