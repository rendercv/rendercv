from ....foundation.base_models import BaseModelWithExtraKeys

# All entry types should inherit from this class.

# This is done to ensure all the entry types use `BaseModelWithExtraKeys` as the
# parent class. Also, other things can be added to all the entry types in the future.


class Entry(BaseModelWithExtraKeys):
    pass
