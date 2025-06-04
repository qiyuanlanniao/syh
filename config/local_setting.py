# -*- coding: utf-8 -*-

# DEBUG 模式开关
# True: 开启 debug 模式，提供更详细的错误信息，方便开发调试
# False: 关闭 debug 模式，通常在生产环境中使用，减少性能损耗和安全风险
DEBUG = True

# SQLAlchemy 的 ECHO 模式开关
# True: SQLAlchemy 会将执行的 SQL 语句打印到控制台，方便调试数据库操作
# False: 关闭 SQL 语句的打印
SQLALCHEMY_ECHO = True

# SQLAlchemy 数据库连接 URI
# 格式：数据库类型+驱动://用户名:密码@主机地址/数据库名?编码
#   - mysql+pymysql: 使用 pymysql 作为 MySQL 驱动
#   - root: 数据库用户名
#   - 123456: 数据库密码
#   - 127.0.0.1: 数据库主机地址 (localhost)
#   - food_db: 数据库名称
#   - charset=utf8mb4: 指定数据库连接的字符集为 utf8mb4，支持更广泛的字符
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1/food_db?charset=utf8mb4'

# SQLAlchemy 的追踪修改选项
# False: 关闭对模型对象修改的追踪，可以提高性能。通常建议关闭。
# True: 开启追踪，会消耗更多内存和资源。
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLAlchemy 连接池的大小
# 设置连接池中保持的连接数。 默认为数据库连接数的上限。
#  当需要数据库连接时，会从连接池中获取，避免频繁创建连接的开销。
SQLALCHEMY_POOL_SIZE = 10

# SQLAlchemy 连接池的最大溢出数量
# 设置连接池允许的最大连接数超过 pool_size 的数量。
# 当连接池中的连接都被占用时，允许创建新的连接，但不能超过 max_overflow。
# 当连接被释放后，如果连接数仍然超过 pool_size，则这些额外的连接会被关闭。
SQLALCHEMY_MAX_OVERFLOW = 5

# SQLAlchemy 数据库编码
# 指定数据库的编码格式。 utf8mb4 支持更广泛的字符，包括 emoji。
SQLALCHEMY_ENCODING = "utf8mb4"

# JSON 序列化时是否使用 ASCII 编码
# False: 不使用 ASCII 编码，支持中文等非 ASCII 字符的显示
# True: 使用 ASCII 编码，会将中文等字符转义成 Unicode 编码
JSON_AS_ASCII = False

# 应用程序的版本号
# 用于追踪应用程序的发布版本，方便回溯和维护
# 格式可以自定义，这里是一个日期+序号的格式
RELEASE_VERSION = "20250414001"