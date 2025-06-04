# -*- coding: utf-8 -*-
from flask import request, jsonify, g

from application import db
from common.libs.Helper import getCurrentDate
from common.models.member.MemberAddress import MemberAddress
from web.controllers.api import route_api


@route_api.route("/my/address/index")
def myAddressList():
    """
    获取我的地址列表
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # 获取当前会员信息，g对象是在请求上下文中共享数据的
    member_info = g.member_info
    # 从数据库中查询会员地址，status=1表示有效地址，member_id是当前会员的ID
    # 按照ID降序排列，返回所有符合条件的地址信息
    list = MemberAddress.query.filter_by(status=1, member_id=member_info.id) \
        .order_by(MemberAddress.id.desc()).all()
    data_list = []
    # 如果查询到地址信息
    if list:
        # 遍历地址列表
        for item in list:
            # 组装地址信息
            tmp_data = {
                "id": item.id,
                "nickname": item.nickname,
                "mobile": item.mobile,
                "is_default": item.is_default,
                # 拼接完整的地址信息
                "address": "%s%s%s%s" % (item.province_str, item.city_str, item.area_str, item.address),
            }
            # 将组装好的地址信息添加到列表中
            data_list.append(tmp_data)
    # 将地址列表添加到返回结果中
    resp['data']['list'] = data_list
    # 返回JSON格式的响应
    return jsonify(resp)


@route_api.route("/my/address/set", methods=["POST"])
def myAddressSet():
    """
    设置我的地址（新增或修改）
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # 获取POST请求中的参数
    req = request.values
    # 获取地址ID，如果存在则转换为int类型，否则默认为0
    id = int(req['id']) if 'id' in req and req['id'] else 0
    # 获取联系人姓名，如果存在则获取，否则默认为空字符串
    nickname = req['nickname'] if 'nickname' in req else ''
    # 获取详细地址，如果存在则获取，否则默认为空字符串
    address = req['address'] if 'address' in req else ''
    # 获取手机号码，如果存在则获取，否则默认为空字符串
    mobile = req['mobile'] if 'mobile' in req else ''

    # 获取省份ID，如果存在则转换为int类型，否则默认为0
    province_id = int(req['province_id']) if ('province_id' in req and req['province_id']) else 0
    # 获取省份名称，如果存在则获取，否则默认为空字符串
    province_str = req['province_str'] if 'province_str' in req else ''
    # 获取城市ID，如果存在则转换为int类型，否则默认为0
    city_id = int(req['city_id']) if ('city_id' in req and req['city_id']) else 0
    # 获取城市名称，如果存在则获取，否则默认为空字符串
    city_str = req['city_str'] if 'city_str' in req else ''
    # 获取区域ID，如果存在则转换为int类型，否则默认为0
    district_id = int(req['district_id']) if ('district_id' in req and req['district_id']) else 0
    # 获取区域名称，如果存在则获取，否则默认为空字符串
    district_str = req['district_str'] if 'district_str' in req else ''

    # 获取当前会员信息
    member_info = g.member_info

    # 校验参数
    if not nickname:
        resp['code'] = -1
        resp['msg'] = "请填写联系人姓名~~"
        return jsonify(resp)

    if not mobile:
        resp['code'] = -1
        resp['msg'] = "请填写手机号码~~"
        return jsonify(resp)

    if province_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择地区~~"
        return jsonify(resp)

    if city_id < 1:
        resp['code'] = -1
        resp['msg'] = "请选择地区~~"
        return jsonify(resp)

    if district_id < 1:
        district_str = ''

    if not address:
        resp['code'] = -1
        resp['msg'] = "请填写详细地址~~"
        return jsonify(resp)

    if not member_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 根据ID和会员ID查询地址信息，判断是新增还是修改
    address_info = MemberAddress.query.filter_by(id=id, member_id=member_info.id).first()
    # 如果存在，则是修改操作
    if address_info:
        model_address = address_info
    # 否则是新增操作
    else:
        # 查询当前会员是否已经有默认地址
        default_address_count = MemberAddress.query.filter_by(is_default=1, member_id=member_info.id, status=1).count()
        # 创建新的地址对象
        model_address = MemberAddress()
        # 设置会员ID
        model_address.member_id = member_info.id
        # 如果当前会员没有默认地址，则设置当前地址为默认地址
        model_address.is_default = 1 if default_address_count == 0 else 0
        # 设置创建时间
        model_address.created_time = getCurrentDate()

    # 设置地址信息
    model_address.nickname = nickname
    model_address.mobile = mobile
    model_address.address = address
    model_address.province_id = province_id
    model_address.province_str = province_str
    model_address.city_id = city_id
    model_address.city_str = city_str
    model_address.area_id = district_id
    model_address.area_str = district_str
    # 设置更新时间
    model_address.updated_time = getCurrentDate()
    # 将地址对象添加到数据库会话中
    db.session.add(model_address)
    # 提交数据库会话，保存更改
    db.session.commit()
    # 返回JSON格式的响应
    return jsonify(resp)


@route_api.route("/my/address/info")
def myAddressInfo():
    """
    获取地址详情
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # 获取请求参数
    req = request.values
    # 获取地址ID
    id = int(req['id']) if 'id' in req else 0
    # 获取会员信息
    member_info = g.member_info

    # 校验参数
    if id < 1 or not member_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 根据ID查询地址信息
    address_info = MemberAddress.query.filter_by(id=id).first()
    # 如果地址信息不存在
    if not address_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 组装地址信息
    resp['data']['info'] = {
        "nickname": address_info.nickname,
        "mobile": address_info.mobile,
        "address": address_info.address,
        "province_id": address_info.province_id,
        "province_str": address_info.province_str,
        "city_id": address_info.city_id,
        "city_str": address_info.city_str,
        "area_id": address_info.area_id,
        "area_str": address_info.area_str
    }
    # 返回JSON格式的响应
    return jsonify(resp)


@route_api.route("/my/address/ops", methods=["POST"])
def myAddressOps():
    """
    地址操作（删除、设置为默认地址）
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # 获取请求参数
    req = request.values
    # 获取地址ID
    id = int(req['id']) if 'id' in req else 0
    # 获取操作类型（del：删除，default：设置为默认地址）
    act = req['act'] if 'act' in req else ''
    # 获取会员信息
    member_info = g.member_info

    # 校验参数
    if id < 1 or not member_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 根据ID和会员ID查询地址信息
    address_info = MemberAddress.query.filter_by(id=id, member_id=member_info.id).first()
    # 如果地址信息不存在
    if not address_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    # 根据操作类型进行处理
    if act == "del":
        # 删除地址，将状态设置为0
        address_info.status = 0
        # 设置更新时间
        address_info.updated_time = getCurrentDate()
        # 添加到数据库会话中
        db.session.add(address_info)
        # 提交数据库会话
        db.session.commit()
    elif act == "default":
        # 设置为默认地址
        # 将当前会员的所有地址的默认状态设置为0
        MemberAddress.query.filter_by(member_id=member_info.id) \
            .update({'is_default': 0})
        # 将当前地址设置为默认地址
        address_info.is_default = 1
        # 设置更新时间
        address_info.updated_time = getCurrentDate()
        # 添加到数据库会话中
        db.session.add(address_info)
        # 提交数据库会话
        db.session.commit()
    # 返回JSON格式的响应
    return jsonify(resp)