from django.db import models

class QuerySetManager(models.Manager):
    def __getattr__(self, name, *args):
        if name.startswith('_'):
            raise AttributeError
        return getattr(self.get_query_set(), name, *args)

    def get_query_set(self):
        return self.model.QuerySet(self.model)
