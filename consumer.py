# consumer.py - 发推机器人
# 这个程序负责从队列中获取内容并处理（例如，发推）。

import redis
import json
import time

# 连接到本地 Redis 服务
try:
    r = redis.Redis(decode_responses=True)
    r.ping()
    print("成功连接到 Redis！")
except redis.exceptions.ConnectionError as e:
    print(f"无法连接到 Redis，请确保 Redis 服务正在运行: {e}")
    exit()

def send_tweet(content):
    """模拟发送推文的函数。"""
    print("\n正在调用 Twitter API...")
    print(f"发推内容: '{content}'")
    # 在这里，你应该集成真实的 Twitter API 客户端库 (如 tweepy)
    # response = twitter_client.create_tweet(text=content)
    time.sleep(2) # 模拟网络延迟
    print("推文发送成功！")

if __name__ == "__main__":
    print("发推机器人已启动，正在等待任务...")
    while True:
        try:
            # brpop 是一个阻塞操作，它会一直等待直到队列中有新消息
            # '0' 表示无限期等待
            # 它返回一个元组 (队列名, 消息内容)
            source_queue, task_json = r.brpop('tweet_queue', 0)
            
            task = json.loads(task_json)
            
            print(f"\n[{time.ctime()}] 从队列 '{source_queue}' 收到新任务。")
            
            # 从任务中提取需要发送的文本
            tweet_text = task.get("message")
            
            if tweet_text:
                send_tweet(tweet_text)
            else:
                print("错误：任务中没有找到 'message' 字段。")

        except redis.exceptions.ConnectionError as e:
            print(f"与 Redis 的连接断开，正在尝试重连... ({e})")
            time.sleep(5)
        except Exception as e:
            print(f"处理任务时发生未知错误: {e}")
            # 你可以在这里将失败的任务记录到日志或另一个“死信队列”中
            time.sleep(5)

