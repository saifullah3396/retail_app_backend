"""
Defines the models of this application.
"""

import base64
import pickle
import uuid

from django.db import models


class DensityHistogram(models.Model):
    """
    A model of a single density histogram (Heatmap) associated with a block
    """

    """Unique uuid for each heatmap."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    """Histogram data in compressed format."""
    data = models.BinaryField()

    """Block with which this histogram is associated."""
    block = models.ForeignKey(
        'locations.Block',
        on_delete=models.CASCADE,
    )

    """Time at which the field was created."""
    created_at = models.DateTimeField(auto_now_add=True)

    def set_data_from_np_arr(self, arr):
        """
        Creates binary data from a numpy array matrix
        """
        data = base64.b64encode(pickle.dumps(arr))

    def get_data_as_np_arr(self):
        """
        Creates a numpy array matrix from binary data
        """
        return pickle.loads(base64.b64decode(data))
