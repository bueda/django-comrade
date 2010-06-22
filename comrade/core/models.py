from django.db import models

class ComradeBaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()

    class Meta:
        abstract = True
        get_latest_by = 'created'
        ordering = ["-created",]

    def get_absolute_url(self, *args, **kwargs):
        return self.get_url_path(*args, **kwargs)
