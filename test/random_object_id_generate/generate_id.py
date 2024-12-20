"""
    used for testing.
"""

import string
import secrets
from bson.objectid import ObjectId

def random_object_id():
    """used for testing.

    Returns:
        Returns: random Object id.
    """
    alphabet = 'abcdef' + string.digits
    _id = ObjectId("".join(secrets.choice(alphabet) for _ in range(24)))
    return _id
