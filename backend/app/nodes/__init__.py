import os
import importlib

for filename in os.listdir(os.path.dirname(__file__)):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f".{filename[:-3]}"
        importlib.import_module(module_name, package=__name__)