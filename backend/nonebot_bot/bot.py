"""
NoneBot 机器人主文件
用于接收外部 HTTP 请求并发送 QQ 消息
"""
import nonebot
from nonebot.adapters.onebot.v11 import Adapter

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(Adapter)

# 加载插件
nonebot.load_plugins("plugins")

# 运行应用
if __name__ == "__main__":
    nonebot.run()
