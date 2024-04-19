from apps.ml.models.base import Model

__all__ = ["Model"]

try:
    from apps.ml.models.surprise import SVDModel

    __all__ += ["SVDModel"]
except ImportError:
    pass
