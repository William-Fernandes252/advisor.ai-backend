import numpy as np
from django.core.serializers.json import DjangoJSONEncoder


class ValidationResultsJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return str(obj.tolist())
        return super().default(obj)
