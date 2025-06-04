# -*- coding: utf-8 -*-
import datetime

from flask import g, render_template

'''
自定义分页类 iPagination

此函数用于生成分页所需的各种参数，方便在前端页面进行分页显示。
它接受一个包含分页参数的字典，并返回一个包含计算结果的字典。

参数：
    params (dict): 一个包含分页参数的字典，包括：
        - total (int): 总记录数。
        - page_size (int): 每页显示的记录数。
        - page (int): 当前页码。
        - display (int): 显示的分页链接数量（例如，显示前后各多少页）。
        - url (str):  带有分页参数的URL，用于生成分页链接。

返回值：
    dict: 一个包含分页信息的字典，包括：
        - is_prev (int): 是否有上一页 (1: 有, 0: 无)。
        - is_next (int): 是否有下一页 (1: 有, 0: 无)。
        - from (int): 分页链接的起始页码。
        - end (int): 分页链接的结束页码。
        - current (int): 当前页码。
        - total_pages (int): 总页数。
        - page_size (int): 每页显示的记录数。
        - total (int): 总记录数。
        - url (str): 带有分页参数的URL。
        - range (range): 一个包含分页链接页码的range对象，方便在模板中循环生成链接。
'''


def iPagination(params):
    import math

    ret = {
        "is_prev": 1,  # 默认有上一页
        "is_next": 1,  # 默认有下一页
        "from": 0,  # 分页链接的起始页码
        "end": 0,  # 分页链接的结束页码
        "current": 0,  # 当前页码
        "total_pages": 0,  # 总页数
        "page_size": 0,  # 每页显示的记录数
        "total": 0,  # 总记录数
        "url": params['url']  # 带有分页参数的URL
    }

    total = int(params['total'])  # 总记录数
    page_size = int(params['page_size'])  # 每页显示的记录数
    page = int(params['page'])  # 当前页码
    display = int(params['display'])  # 显示的分页链接数量
    total_pages = int(math.ceil(total / page_size))  # 计算总页数，向上取整
    total_pages = total_pages if total_pages > 0 else 1  # 如果总页数为0，则设置为1

    # 判断是否有上一页
    if page <= 1:
        ret['is_prev'] = 0  # 如果当前页是第一页，则没有上一页

    # 判断是否有下一页
    if page >= total_pages:
        ret['is_next'] = 0  # 如果当前页是最后一页，则没有下一页

    semi = int(math.ceil(display / 2))  # 计算半个显示链接数，用于确定起始和结束页码

    # 计算起始页码
    if page - semi > 0:
        ret['from'] = page - semi
    else:
        ret['from'] = 1  # 如果起始页码小于1，则设置为1

    # 计算结束页码
    if page + semi <= total_pages:
        ret['end'] = page + semi
    else:
        ret['end'] = total_pages  # 如果结束页码大于总页数，则设置为总页数

    ret['current'] = page  # 设置当前页码
    ret['total_pages'] = total_pages  # 设置总页数
    ret['page_size'] = page_size  # 设置每页显示的记录数
    ret['total'] = total  # 设置总记录数
    ret['range'] = range(ret['from'], ret['end'] + 1)  # 生成一个包含分页链接页码的range对象，方便在模板中循环生成链接
    return ret


'''
统一渲染方法 ops_render

此函数用于统一渲染模板，将一些公共变量传递给模板。

参数：
    template (str): 模板文件名。
    context (dict):  传递给模板的上下文数据，默认为空字典。

返回值：
    str: 渲染后的模板内容。
'''


def ops_render(template, context={}):
    # 如果g对象中存在current_user，则将其添加到上下文中
    if 'current_user' in g:
        context['current_user'] = g.current_user
    # 使用Flask的render_template函数渲染模板，并将上下文数据传递给模板
    return render_template(template, **context)


def getCurrentDate(format="%Y-%m-%d %H:%M:%S"):
    # 使用datetime模块获取当前时间，并使用strftime方法格式化
    currentTime = datetime.datetime.now().strftime(format)
    return currentTime


#  根据某个字段获取一个dict出来 getDictFilterField
#  将一个模型对象列表转换为字典，字典的键是列表中每个对象的指定字段值。
#  适用于根据ID列表查询模型对象，并将其组织成字典，方便快速查找。

#  参数：
#      db_model (SQLAlchemy模型): SQLAlchemy模型类，用于查询数据库。
#      select_field (SQLAlchemy列): 用于过滤查询的字段（例如，db_model.id）。
#      key_field (str):  模型对象中作为字典键的字段名（例如，'id'）。
#      id_list (list):  一个包含要查询的ID的列表。

#  返回值：
#      dict: 一个字典，其中键是模型对象的key_field的值，值是对应的模型对象。

def getDictFilterField(db_model, select_field, key_field, id_list):
    ret = {}  # 初始化返回字典
    query = db_model.query  # 创建查询对象
    # 如果id_list不为空且长度大于0，则添加过滤条件
    if id_list and len(id_list) > 0:
        query = query.filter(select_field.in_(id_list))  # 使用in_方法过滤查询，只查询select_field在id_list中的记录

    list = query.all()  # 执行查询，获取所有符合条件的记录列表

    if not list:  # 如果列表为空，则直接返回空字典
        return ret
    for item in list:  # 遍历查询结果列表
        if not hasattr(item, key_field):  # 检查模型对象是否包含指定的key_field属性
            break  # 如果不包含，则跳出循环（通常意味着数据结构不一致）
        ret[getattr(item, key_field)] = item  # 将模型对象的key_field属性值作为键，模型对象本身作为值，存入字典
    return ret  # 返回生成的字典


# 从对象列表中提取指定字段的值，并去重 selectFilterObj
# 用于从一个对象列表中提取某个字段的值，并将提取的值去重后返回。
# 常用于获取一组不重复的属性值，例如，从一组用户对象中获取所有的用户角色。

# 参数：
#      obj (list):  一个包含对象的列表，每个对象都应该有相同的字段。
#      field (str):  要提取的字段名。

# 返回值：
#      list: 一个包含提取的字段值的列表，并且已经去重。

def selectFilterObj(obj, field):
    ret = []  # 初始化返回列表
    for item in obj:  # 遍历对象列表
        if not hasattr(item, field):  # 检查对象是否包含指定的field属性
            continue  # 如果不包含，则跳过当前对象
        if getattr(item, field) in ret:  # 检查当前字段值是否已经存在于返回列表中
            continue  # 如果已经存在，则跳过当前对象，避免重复添加
        ret.append(getattr(item, field))  # 将当前对象的指定字段值添加到返回列表中
    return ret  # 返回去重后的字段值列表


#  根据某个字段获取一个dict出来,value 为列表 getDictListFilterField
#  与getDictFilterField类似，但它将具有相同key_field值的对象放入一个列表中，作为字典的值。
#  适用于需要根据某个字段对模型对象进行分组的场景。

#  参数：
#      db_model (SQLAlchemy模型): SQLAlchemy模型类，用于查询数据库。
#      select_filed (SQLAlchemy列): 用于过滤查询的字段（例如，db_model.id）。
#      key_field (str):  模型对象中作为字典键的字段名（例如，'id'）。
#      id_list (list):  一个包含要查询的ID的列表。

#  返回值：
#      dict: 一个字典，其中键是模型对象的key_field的值，值是一个包含具有相同key_field值的模型对象列表。

def getDictListFilterField(db_model, select_filed, key_field, id_list):
    ret = {}  # 初始化返回字典
    query = db_model.query  # 创建查询对象
    # 如果id_list不为空且长度大于0，则添加过滤条件
    if id_list and len(id_list) > 0:
        query = query.filter(select_filed.in_(id_list))  # 使用in_方法过滤查询，只查询select_filed在id_list中的记录

    list = query.all()  # 执行查询，获取所有符合条件的记录列表
    if not list:  # 如果列表为空，则直接返回空字典
        return ret
    for item in list:  # 遍历查询结果列表
        if not hasattr(item, key_field):  # 检查模型对象是否包含指定的key_field属性
            break  # 如果不包含，则跳出循环（通常意味着数据结构不一致）
        if getattr(item, key_field) not in ret:  # 检查当前key_field的值是否已经存在于字典中
            ret[getattr(item, key_field)] = []  # 如果不存在，则创建一个新的空列表作为该键的值

        ret[getattr(item, key_field)].append(item)  # 将当前模型对象添加到对应key_field值的列表中
    return ret  # 返回生成的字典


def getFormatDate(date=None, format="%Y-%m-%d %H:%M:%S"):
    if date is None:  # 如果没有传入日期对象，则使用当前时间
        date = datetime.datetime.now()

    return date.strftime(format)  # 使用strftime方法格式化日期对象