from ..database.Source import Source
from ..database.FirestoreAccessor import FirestoreAccessor, QueryFilter

class FirestoreSource(Source):

    def __init__(self, parents, last_id: str = None, filter_type: str = None, filter_str: str = None):
        super().__init__(parents, last_id, filter_str)
        query_filter = QueryFilter.NONE
        if filter_type:
            try:
                query_filter = QueryFilter[filter_type.upper()]
            except KeyError:
                raise KeyError("Invalid filter_type provided")


        self.set_database(FirestoreAccessor(filter=query_filter))

    def register_shared(self, manager):
        manager.register_executor('FirestoreSource', self)

    def share(self, manager):
        return manager.FirestoreSource()
