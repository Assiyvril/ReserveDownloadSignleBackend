#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @author chencody@qq.com
# @date 2023/3/3
# @file pagination.py
# @remark 自定义分页类

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

"""
自定义的分页数据结构
参数:
pageNo - 页码
pageSize - 每页数量

接收以上参数时触发 (pageSize <= 0 时, 忽略分页)
"""


# 自定义分页回复结果
class CustomV3Pagination(PageNumberPagination):
    # 页面查询字符串
    page_query_param = "pageNo"
    # 页量查询字符串
    page_size_query_param = "pageSize"
    # 最大请求量
    max_page_size = 500

    # 分页数据回复格式
    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "total": self.page.paginator.count
        })
