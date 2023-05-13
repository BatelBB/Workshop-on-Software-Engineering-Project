import sys
import collections
from typing import MutableMapping

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", MutableMapping)