from django.db import models
from django.forms.models import model_to_dict

CateTypeID = (
    (0, u'无'),
    (1, u'毛货'),
    (2, u'净货'),
    (3, u'标品'),
    (4, u'其它'),
)


class ShopCategory(models.Model):
    shop_id = models.IntegerField(verbose_name=u'所属商户', default=2)
    name = models.CharField(u'名称', max_length=31)
    parent = models.ForeignKey('self', verbose_name=u'父类', related_name='children', null=True, blank=True, on_delete=models.SET_NULL)
    level = models.PositiveIntegerField(u'分类级别', default=1, help_text=u'1一级，2二级、3三级、4四级')
    tag = models.CharField(u'备注标准', max_length=31, null=True, blank=True)
    cate_type_id = models.PositiveIntegerField(u'归类', default=0, choices=CateTypeID, help_text=u'毛货、净货、其它')
    is_active = models.BooleanField(u'是否生效', default=True, help_text=u'无效的分类不会在APP中显示')
    order = models.PositiveIntegerField(u'排序', default=200, help_text=u'从小到大显示。请设置合适的大小，以维持树结构。')
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    is_enable = models.BooleanField(default=True, verbose_name='是否启用',
                                    help_text='是否启用, 23-12-15 添加新字段, is_active, 开发完成后,将is_active=false的状态, 同步到到is_enable')
    is_leaf = models.BooleanField(null=True, blank=True, verbose_name='是否叶子节点', help_text='是否叶子节点, 23-12-20 添加新字段, 每当节点变动时, 需要更新此字段')

    class Meta:
        managed = False
        db_table = 'shop_category'
        # unique_together = ('name',)

    @classmethod
    def update_is_leaf(cls, category_id_list):
        # 更新所有叶子节点
        qs = cls.objects.filter(id__in=category_id_list, is_active=True, shop_id=2).all()
        if qs.count() == 0:
            return
        for item in qs:
            children_count = cls.objects.filter(parent_id=item.id, is_active=True, shop_id=2, is_enable=True).count()
            item.is_leaf = True if item.level > 1 and children_count == 0 else False
            item.save()

    # 获取类别目录数
    @classmethod
    def get_category_tree_data(cls, shop=None):
        # 获取所有归属shop的数据
        queryset = ShopCategory.objects.filter(shop_id=shop, is_active=True).order_by('order')

        # 递归生成树形结构数据
        def recursive_categories(categories, parent_id=None):
            result = []
            for category in categories:
                """
                基于dg3品类表历史原因，部分品类(如 标品(id:130, parent_id:95, level:1))属于顶级品类，但是parent_id关联一个已关闭的品类
                因此，不能完全由parent_id判断
                判断条件: parent_id为空默认顶级分类，如果parent_id不为空，但是level=1，忽略parent_id，视为顶级分类
                """
                category_parent_id = None if category.parent_id is None or category.level == 1 else category.parent_id
                if category_parent_id == parent_id:
                    category_dict = model_to_dict(category)
                    category_dict['name'] = f"{category_dict['name']}[{category_dict['tag']}]"
                    children = recursive_categories(categories, category.id)
                    if len(children) > 0:
                        category_dict['children'] = children
                    result.append(category_dict)
            return result

        return recursive_categories(queryset)

    # 获取所有归属于shop=2的已激活目录数据，并按order倒序排列
    @classmethod
    def get_all_category(cls):
        return cls.objects.filter(shop_id=2, is_active=True).order_by('-order').all()

    # +根据当前目录，查找指定层级的父目录
    @classmethod
    def find_category_by_level(cls, categories, target, level):
        # 高于指定层级或没有父几点，直接返回
        if target.level is None or target.level <= level or target.parent_id is None:
            return target
        # 如果存在父节点
        elif target.parent_id is not None:
            # 获取父节点
            parent = next((c for c in categories if c.id == target.parent_id), None)
            if parent is not None:
                return cls.find_category_by_level(categories, parent, level)
            else:
                # 没有对应的父节点
                return target

    def get_my_family(self):
        """
        获取当前节点的家族
        """
        family = []
        node = self
        while node is not None:
            # 将当前节点添加到父级列表
            family.append(node)
            # 移动到下一个父级
            node = node.parent
        # 返回父级列表
        return family[::-1]
