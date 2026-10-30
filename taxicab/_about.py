import importlib.metadata

try:
    __version__ = importlib.metadata.version("Taxicab")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__author__ = "Nathan A. Rooy"

