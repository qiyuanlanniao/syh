# -*- coding: utf-8 -*- # 指定文件编码为UTF-8
# 导入需要的模块
from flask import request, jsonify, g # 从flask框架导入请求对象、JSON响应函数、全局上下文对象g

from application import db # 从自定义模块导入数据库连接对象
from common.libs.Helper import getCurrentDate # 导入获取当前日期时间的辅助函数
from common.libs.member.MemberService import MemberService # 导入会员服务类，包含微信openid获取、盐值生成、授权码生成等方法
from common.models.goods.WxShareHistory import WxShareHistory # 导入微信分享历史记录模型
from common.models.member.Member import Member # 导入会员信息模型
from common.models.member.OauthMemberBind import OauthMemberBind # 导入第三方授权绑定信息模型
from web.controllers.api import route_api # 导入API蓝图对象，用于注册路由


# 定义会员登录接口
# 这个接口用于处理微信小程序用户的登录/注册流程
@route_api.route('/member/login', methods=['GET', 'POST'])
def login():
    # 初始化接口响应数据字典
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    # 获取请求参数，request.values包含了GET和POST的所有参数
    req = request.values
    # 从请求参数中获取微信小程序提供的code，如果不存在则设置为空字符串
    code = req['code'] if 'code' in req else ''
    # 校验code是否为空或长度小于1
    if not code or len(code) < 1:
        # 如果code无效，设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '需要code'
        # 返回错误响应的JSON格式
        return jsonify(resp)

    # 调用会员服务类的方法，使用code去微信后端换取openid等信息
    openid = MemberService.getWeChatOpenId(code)
    # 校验获取的openid是否为空（获取openid失败）
    if openid is None:
        # 如果获取openid失败，设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        # 返回错误响应的JSON格式
        return jsonify(resp)

    # 从请求参数中获取微信用户的昵称、性别和头像URL
    # 这些信息通常在小程序前端通过wx.getUserInfo接口获取并传递给后端
    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0 # 注意：这里的gender在微信小程序返回的是数字，0是未知，1是男性，2是女性
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''

    # 根据获取到的openid和绑定类型（1代表微信小程序）查询数据库中的OauthMemberBind表
    # 判断该openid是否已经绑定过会员账号，即判断用户是否已经注册过
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    # 如果不存在绑定记录（bind_info is None），则说明是新用户，需要进行注册
    if not bind_info:
        # 创建新的Member模型实例，准备插入会员信息
        model_member = Member()
        # 设置新会员的昵称、性别和头像
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        # 为新会员生成一个随机盐值，用于后续密码加密等
        model_member.salt = MemberService.geneSalt()
        # 设置会员的创建时间和更新时间为当前日期时间
        model_member.updated_time = model_member.created_time = getCurrentDate()
        # 将新的会员信息添加到数据库会话中，准备执行插入操作
        db.session.add(model_member)
        # 提交数据库会话，将会员信息保存到数据库
        db.session.commit()

        # 创建新的OauthMemberBind模型实例，准备记录openid与会员ID的绑定关系
        model_bind = OauthMemberBind()
        # 将绑定记录关联到刚刚创建的会员的ID
        model_bind.member_id = model_member.id
        # 设置绑定类型为微信小程序（1）
        model_bind.type = 1
        # 设置绑定的openid
        model_bind.openid = openid
        # 额外的绑定信息，此处为空字符串
        model_bind.extra = ''
        # 设置绑定记录的创建时间和更新时间为当前日期时间
        model_bind.updated_time = model_bind.created_time = getCurrentDate()
        # 将新绑定信息添加到数据库会话中
        db.session.add(model_bind)
        # 提交数据库会话，将绑定信息保存到数据库
        db.session.commit()

        # 将刚刚创建的绑定记录赋值给bind_info变量，以便后续统一处理
        bind_info = model_bind

    # 根据绑定记录中的member_id（无论是新创建的还是已存在的）查询对应的会员信息
    member_info = Member.query.filter_by(id=bind_info.member_id).first()

    # 生成用户认证token
    # Token的格式是将一个根据用户信息生成的授权码与会员ID拼接起来，用#分隔
    # 这样在后续请求中，可以通过解析token获取会员ID，并通过授权码验证token的有效性
    token = f"{MemberService.geneAuthCode(member_info)}#{member_info.id}"
    # 将生成的token放到响应数据的data字段中，返回给前端
    resp['data'] = {'token': token}

    # 返回包含token的成功JSON响应
    return jsonify(resp)


# 定义检查会员是否已注册（绑定）接口
# 这个接口用于小程序启动时快速检查用户是否已注册，如果已注册则直接返回token
@route_api.route("/member/check-reg", methods=["GET", "POST"])
def checkReg():
    # 初始化接口响应数据字典
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    # 获取请求参数
    req = request.values
    # 从请求参数中获取微信小程序的code
    code = req['code'] if 'code' in req else ''
    # 校验code是否为空或长度小于1
    if not code or len(code) < 1:
        # 如果code无效，设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = "需要code"
        # 返回错误响应
        return jsonify(resp)

    # 调用会员服务获取微信用户的openid
    openid = MemberService.getWeChatOpenId(code)
    # 校验获取的openid是否为空
    if openid is None:
        # 如果获取openid失败，设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = "调用微信出错"
        # 返回错误响应
        return jsonify(resp)

    # 根据openid和类型（1代表微信小程序）查询是否已存在绑定记录
    bind_info = OauthMemberBind.query.filter_by(openid=openid, type=1).first()
    # 如果不存在绑定记录，说明该openid未绑定会员，即用户未注册
    if not bind_info:
        # 设置错误码为-1，表示未绑定
        resp['code'] = -1
        resp['msg'] = "未绑定"
        # 返回错误响应
        return jsonify(resp)

    # 如果存在绑定记录，根据绑定记录中的member_id查询对应的会员信息
    member_info = Member.query.filter_by(id=bind_info.member_id).first()
    # 校验是否成功查询到会员信息
    if not member_info:
        # 理论上如果绑定记录存在，会员信息也应该存在，这里是额外的校验
        resp['code'] = -1
        resp['msg'] = "未查询到绑定信息" # 这个错误信息可能有点歧义，可以更精确地说是“未查询到关联的会员信息”
        # 返回错误响应
        return jsonify(resp)

    # 如果找到绑定记录和会员信息，说明用户已注册，生成认证token
    # Token格式：授权码#会员ID
    token = f"{MemberService.geneAuthCode(member_info)}#{member_info.id}"
    # 将生成的token放到响应数据的data字段中
    resp['data'] = {'token': token}
    # 返回包含token的成功JSON响应
    return jsonify(resp)


# 定义会员分享记录接口
# 这个接口用于记录用户在小程序中的分享行为
# 假设这个接口在请求前执行已经通过token验证了用户身份，
# 并将当前登录的会员信息存入全局上下文对象g的g.member_info属性中
@route_api.route("/member/share", methods=['POST'])
def memberShare():
    # 初始化接口响应数据字典
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    # 获取请求参数
    req = request.values
    # 从请求参数中获取分享的URL，如果不存在则设置为空字符串
    url = req['url'] if 'url' in req else ''
    # 从全局上下文g中获取当前登录的会员信息
    member_info = g.member_info
    # 创建WxShareHistory模型实例，用于记录分享行为
    model_share = WxShareHistory()
    # 如果会员信息存在（用户已登录），则记录分享行为关联的会员ID
    if member_info:
        model_share.member_id = member_info.id

    # 记录分享的URL
    model_share.share_url = url
    # 记录分享发生的时间为当前日期时间
    model_share.created_time = getCurrentDate()
    # 将新分享记录添加到数据库会话
    db.session.add(model_share)
    # 提交数据库会话，将分享记录保存到数据库
    db.session.commit()
    # 返回成功的JSON响应
    return jsonify(resp)


# 定义获取会员信息接口
# 这个接口用于获取当前登录用户的基本信息
# 同样假设会员信息已通过验证存入g.member_info
@route_api.route("/member/info") # 默认允许的请求方法是GET
def memberInfo():
    # 初始化接口响应数据字典
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    # 从全局上下文g中获取当前登录的会员信息
    member_info = g.member_info
    # 将会员的昵称和头像URL组织成一个字典，并放入响应数据的info字段中
    resp['data']['info'] = {
        "nickname": member_info.nickname,
        "avatar_url": member_info.avatar
    }
    # 返回包含会员信息的JSON响应
    return jsonify(resp)