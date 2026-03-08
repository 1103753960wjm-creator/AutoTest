from email.policy import default
from tortoise import fields, Model
from urllib3 import response


class Mitmproxy_api(Model):
    result_id = fields.CharField(max_length=255, description="结果id")
    device = fields.ForeignKeyField("models.App_device")
    url = fields.TextField(description="接口请求地址", default="")
    method = fields.CharField(max_length=255, description="请求方法", default="POST")
    request_body = fields.JSONField(description="请求体", default={})
    request_headers = fields.JSONField(description="请求头", default={})
    response_headers = fields.JSONField(description="响应头", default={})
    response_body = fields.JSONField(description="响应体", default={})
    status = fields.IntField(description="状态", default=0)
    res_time = fields.TextField(description="响应时间", default="")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
