import requests
import json
from polymorphic.models import PolymorphicModel, PolymorphicManager
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urljoin
from django.db import models
from .base import BaseModel
from jsonfield import JSONField
# patch
PolymorphicModel.polymorphic_ctype = models.ForeignKey(
        ContentType,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name="polymorphic_%(app_label)s.%(class)s_set+",
    )
EXPECT_BODY_MODE_JSON_KV = 'json-kv'
EXPECT_BODY_MODE_TEXT_RE = 'text-re'
EXPECT_BODY_TYPE_CHOICE_TEXT = 'text'
EXPECT_BODY_TYPE_CHOICE_JSON = 'json'


class BaseHook(PolymorphicModel, BaseModel):
    name = models.CharField(max_length=255, blank=False)
    objects = PolymorphicManager()


class HookServer(BaseModel):
    host = models.CharField('host like http://xxxx', max_length=64)
    headers = JSONField('http headers', default={})


class HttpHook(BaseHook):
    export_body_modes = []
    method_choices = (
        ('get', 'get'),
        ('post', 'post'),
        ('delete', 'delete'),
        ('put', 'put')
    )
    http_server = models.ForeignKey(HookServer, on_delete=models.CASCADE, db_constraint=False)
    uri = models.CharField(max_length=255, default='')
    expect_body_type_choice = (
        (EXPECT_BODY_TYPE_CHOICE_JSON, EXPECT_BODY_TYPE_CHOICE_JSON),
        (EXPECT_BODY_TYPE_CHOICE_TEXT, EXPECT_BODY_TYPE_CHOICE_TEXT),
    )
    method = models.CharField('http method', choices=method_choices, max_length=255)
    headers = JSONField('http headers', default={})
    expect_code = models.IntegerField('expect http response code', default=None, null=True)
    expect_body_type = models.CharField('expect_body_type', choices=expect_body_type_choice, max_length=255)
    expect_body_json_key = models.CharField(max_length=255, default=None)
    expect_response = models.CharField('expect response', max_length=1024, default=None)

    def trigger(self, obj):
        headers = {}
        headers.update(self.http_server.headers)
        headers.update(self.headers)
        body = json.dumps(obj)
        r = requests.request(self.method, urljoin(self.http_server.host, self.uri), headers=headers, data=body)
        if self.expect_code is None:
            if r.status_code > 299:
                raise requests.exceptions.RequestException('request failed, response %r' % r.text)
        elif self.expect_code != r.status_code:
            raise requests.exceptions.RequestException('request failed, response %r' % r.text)
        elif self.expect_body_type == EXPECT_BODY_TYPE_CHOICE_JSON:
            self.expect_body_type = EXPECT_BODY_TYPE_CHOICE_JSON
            r = r.json()
            key_ls = self.expect_body_json_key.split('.')
            for x in key_ls:
                r = r.get(x)
            if str(r) != self.expect_response:
                raise requests.exceptions.RequestException('request failed, response %r' % r.text)
        elif self.expect_body_type == EXPECT_BODY_TYPE_CHOICE_TEXT:
            r = r.text
            if r.strip() != self.expect_response.strip():
                raise requests.exceptions.RequestException('request failed, response %r' % r.text)
        return

