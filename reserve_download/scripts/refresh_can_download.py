"""
2024-04-22
对新增的 can_download 字段进行刷新，刷新规则如下：
将现有的 is_success 字段为 True 的记录， 全部将 can_download 字段置为 True
"""
import json
from scripts_public import _setup_django
from reserve_download.models import ReserveDownload


def refresh_can_download():
    qs = ReserveDownload.objects.filter(is_success=True)
    id_list = qs.values_list('id', flat=True)
    # 保险起见， 将本次操作的 id list 保存为 json 文件
    with open('refresh_candownload_id_list.json', 'w') as f:
        json.dump(list(id_list), f)
    print(f'本次操作的 id list 已保存到 refresh_candownload_id_list.json 文件中')
    print(f'共有{qs.count()}条记录需要更新')
    qs.update(can_download=True)
    print('更新完毕')


if __name__ == '__main__':
    refresh_can_download()
