#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @author chencody@qq.com
# @date 2023/3/3
# @file rederer.py
# @remark 自定义回复结构类


from rest_framework import status
from rest_framework.renderers import JSONRenderer

"""
自定义的Response回复格式:
{
        code: number,  // 请求返回代码
        data: any,     // 返回数据内容
        msg: string    // 错误信息，code:200时, msg默认为success
}
"""


# 自定义JSON处理类
class CustomV3Renderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # 统一格式化
        response = renderer_context['response']
        status_code = response.status_code
        format_response = {
            "code": 200,
            "data": data,
            "msg": "success",
            "mark": 'v3'
        }
        if status_code >= status.HTTP_400_BAD_REQUEST:
            # 异常情况处理
            format_response["code"] = status_code
            format_response['data'] = {}
            format_response["msg"] = ""
            if isinstance(data, dict):
                for key in data:
                    format_response["msg"] += f"{key}:{data[key]};"
            else:
                format_response["msg"] = data
        else:
            # 小于400的代码，重置返回码为200
            setattr(response, "status_code", status.HTTP_200_OK)
        return super().render(format_response, accepted_media_type, renderer_context)
