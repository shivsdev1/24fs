import os
import importlib


def load_commands(bot):
    for filename in os.listdir("commands"):
        if filename.endswith(".py") and filename not in ("__init__.py", "loader.py"):
            module_name = f"commands.{filename[:-3]}"
            module = importlib.import_module(module_name)

            if hasattr(module, "setup"):
                module.setup(bot)