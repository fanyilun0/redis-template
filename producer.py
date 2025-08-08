# producer.py - 监控服务
# 这个程序负责生成内容并将其发送到队列中。

import redis
import json
import time
import random

# 连接到本地 Redis 服务
# decode_responses=True 确保我们从 Redis 获取的是字符串而不是字节
try:
    r = redis.Redis(decode_responses=True)
    r.ping()
    print("成功连接到 Redis！")
except redis.exceptions.ConnectionError as e:
    print(f"无法连接到 Redis，请确保 Redis 服务正在运行: {e}")
    exit()

def monitor_service():
    """模拟一个监控服务，随机生成事件。"""
    services = ["数据库服务", "Web 服务器", "API 网关"]
    service_name = random.choice(services)
    event = {
        "service": service_name,
        "status": "DOWN",
        "message": f"警报！检测到 {service_name} 已于 {time.ctime()} 掉线。",
        "timestamp": time.time()
    }
    return event

if __name__ == "__main__":
    # 模拟生成一个事件
    content_to_tweet = monitor_service()
    
    # 将内容打包成 JSON 字符串推入名为 'tweet_queue' 的队列
    # lpush 从列表左侧推入
    r.lpush('tweet_queue', json.dumps(content_to_tweet))
    
    print(f"消息已发送到队列: {content_to_tweet['message']}")

# ===================================================================

