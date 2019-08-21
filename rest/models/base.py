from django.db import models
import uuid


class BaseModel(models.Model):
    _ctime = models.DateTimeField(auto_now_add=True)
    _mtime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @staticmethod
    def gen_uuid():
        return uuid.uuid4().hex


