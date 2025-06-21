import importlib, pkgutil
import dapmeet.models as models_pkg
from dapmeet.db.db import Base
for _, module_name, _ in pkgutil.iter_modules(models_pkg.__path__):
    importlib.import_module(f"dapmeet.models.{module_name}")

target_metadata = Base.metadata
