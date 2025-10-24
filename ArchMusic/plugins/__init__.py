# ArchMusic/plugins/__init__.py
# Düzeltilmiş Plugin Yükleyici – Alt klasör hatasını düzeltir

import glob
import os

ALL_MODULES = []

for f in glob.glob("ArchMusic/plugins/*.py"):
    module_name = os.path.basename(f)[:-3]
    if module_name != "__init__":
        ALL_MODULES.append(module_name)

__all__ = ALL_MODULES
