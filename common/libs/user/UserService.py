# -*- coding: utf-8 -*-

import bcrypt  # 导入 bcrypt 库，用于密码哈希和加盐


class UserService():
    """
    UserService 类，提供用户相关的服务，如生成认证码、密码哈希等。
    """

    @staticmethod
    def geneAuthCode(user_info):
        """
        生成用户认证码（Auth Code）。
        这个方法将用户信息的多个字段组合成一个字符串，然后使用 bcrypt 进行哈希。
        这样做是为了生成一个唯一的、安全的认证码，用于验证用户身份。

        Args:
            user_info (UserInfo): 包含用户信息的 UserInfo 对象。

        Returns:
            str: 生成的认证码（哈希后的字符串）。
        """
        # 将用户信息的各个部分（uid、login_name、login_pwd、login_salt）组合成一个字符串
        # 使用 f-string 方便地进行字符串格式化
        raw_string = f"{user_info.uid}-{user_info.login_name}-{user_info.login_pwd}-{user_info.login_salt}"

        # 将字符串编码为 UTF-8 字节串，因为 bcrypt 需要字节串作为输入
        raw_bytes = raw_string.encode("utf-8")

        # bcrypt.hashpw 函数需要 salt 也为字节串，将 user_info 中的 login_salt 编码为字节串
        user_salt = user_info.login_salt.encode('utf-8')

        # 使用 bcrypt.hashpw 函数对原始字节串进行哈希，使用用户特定的 salt
        # bcrypt.hashpw 会自动将 salt 添加到哈希结果中，方便后续验证
        hashed_bytes = bcrypt.hashpw(raw_bytes, user_salt)

        # 将哈希后的字节串解码为 UTF-8 字符串，便于存储和传输
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def genePwd(pwd, salt):
        """
        生成密码哈希值。
        这个方法使用 bcrypt 对用户提供的密码进行哈希，并使用提供的 salt。
        这个方法用于在用户注册或修改密码时，对密码进行安全存储。

        Args:
            pwd (str): 用户提供的原始密码。
            salt (str): 用于哈希密码的 salt 值。

        Returns:
            str: 哈希后的密码字符串。
        """
        password_bytes = pwd.encode('utf-8')  # 将密码编码为 UTF-8 字节串

        user_salt = salt.encode('utf-8')  # 将 salt 编码为 UTF-8 字节串

        # 使用 bcrypt.hashpw 函数对密码字节串进行哈希，使用提供的 salt
        hashed_password = bcrypt.hashpw(password_bytes, user_salt)
        return hashed_password.decode('utf-8')  # 返回字符串形式的哈希值

    @staticmethod
    def geneSalt():
        """
        生成一个随机的 salt 值。
        salt 值用于增加密码哈希的安全性，防止彩虹表攻击。
        bcrypt.gensalt() 函数会生成一个随机的、安全的 salt 值。

        Returns:
            bytes: 生成的 salt 值（字节串）。
        """
        return bcrypt.gensalt() # 返回 salt 值，类型为 bytes。一般保存为字符串

class UserInfo:  # 定义一个类来表示用户信息
    """
    UserInfo 类，用于存储用户的基本信息。
    """
    def __init__(self, uid, login_name, login_pwd, login_salt):
        """
        初始化 UserInfo 对象。

        Args:
            uid (int): 用户 ID。
            login_name (str): 登录名。
            login_pwd (str): 登录密码。
            login_salt (str): 用于密码哈希的 salt 值。
        """
        self.uid = uid  # 用户ID
        self.login_name = login_name  # 登录名
        self.login_pwd = login_pwd  # 登录密码（哈希后的密码）
        self.login_salt = login_salt  # 盐值

# 创建 UserInfo 类的实例
user_info = UserInfo(
    uid=1,  # 用户ID
    login_name="admin123",  # 登录名
    login_pwd="123456",  # 登录密码
    login_salt="$2b$12$uiZuMjMUqXnOFDsa2X/lXO"  # 盐值
)
pwd = "123456"  # 原始密码
salt = "$2b$12$uiZuMjMUqXnOFDsa2X/lXO"  # 盐值

# 测试代码（取消注释后可以运行）
# print(UserService.genePwd(pwd, salt)) #  将密码“123456”进行bcrypt加密，$2b$12$uiZuMjMUqXnOFDsa2X/lXO为盐
# print(UserService.geneAuthCode(user_info)) # 将user_info里的login_name，login_pwd，login_salt组合之后进行bcrypt加密