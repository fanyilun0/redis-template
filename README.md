# Redis 消息队列测试项目

这是一个基于Redis的简单消息队列系统，包含生产者(producer)和消费者(consumer)两个组件，用于演示服务监控告警的自动化推送流程。

## 项目结构

```
redis/
├── producer.py     # 生产者 - 监控服务，生成告警消息
├── consumer.py     # 消费者 - 发推机器人，处理队列中的消息
├── requirements.txt # Python依赖包
└── README.md       # 项目说明文档
```

## 功能说明

### Producer (producer.py)
- **功能**: 模拟监控服务，检测系统状态并生成告警消息
- **作用**: 当检测到服务异常时，将告警信息发送到Redis队列
- **队列**: 使用 `tweet_queue` 队列存储待处理的消息

### Consumer (consumer.py)
- **功能**: 模拟发推机器人，持续监听队列并处理消息
- **作用**: 从Redis队列中获取告警消息，模拟发送到Twitter
- **特点**: 使用阻塞式操作(`brpop`)，实时处理新消息

## 环境要求

- Python 3.6+
- Redis 服务器

## 安装步骤

### 1. 安装Redis服务器

**Windows:**
```bash
# 下载Redis for Windows或使用Docker
docker run -d -p 6379:6379 redis:latest
```

**MacOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 启动和测试

### 方法一：手动测试

1. **启动Redis服务**
   ```bash
   # 检查Redis是否运行
   redis-cli ping
   # 应该返回 PONG
   ```

2. **启动消费者(在终端1中)**
   ```bash
   python consumer.py
   ```
   输出示例：
   ```
   成功连接到 Redis！
   发推机器人已启动，正在等待任务...
   ```

3. **运行生产者(在终端2中)**
   ```bash
   python producer.py
   ```
   输出示例：
   ```
   成功连接到 Redis！
   消息已发送到队列: 警报！检测到 数据库服务 已于 Mon Jan 15 10:30:45 2024 掉线。
   ```

4. **观察消费者输出**
   消费者终端应该显示：
   ```
   [Mon Jan 15 10:30:45 2024] 从队列 'tweet_queue' 收到新任务。

   正在调用 Twitter API...
   发推内容: '警报！检测到 数据库服务 已于 Mon Jan 15 10:30:45 2024 掉线。'
   推文发送成功！
   ```

### 方法二：批量测试

多次运行生产者来测试队列处理：

```bash
# 快速发送多条消息
for i in {1..5}; do python producer.py; sleep 1; done
```

## 队列操作说明

### 查看队列状态
```bash
# 连接Redis CLI
redis-cli

# 查看队列长度
LLEN tweet_queue

# 查看队列内容(不移除)
LRANGE tweet_queue 0 -1

# 清空队列
DEL tweet_queue
```

### 手动添加测试消息
```bash
redis-cli
LPUSH tweet_queue '{"service":"测试服务","status":"DOWN","message":"这是一条测试消息","timestamp":1642234567}'
```

## 扩展功能

### 1. 集成真实Twitter API
在 `consumer.py` 中的 `send_tweet()` 函数内：
```python
import tweepy

# 配置Twitter API
api = tweepy.Client(
    bearer_token="your_bearer_token",
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    access_token="your_access_token",
    access_token_secret="your_access_token_secret"
)

def send_tweet(content):
    try:
        response = api.create_tweet(text=content)
        print(f"推文发送成功！Tweet ID: {response.data['id']}")
    except Exception as e:
        print(f"发送推文失败: {e}")
```

### 2. 添加日志记录
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. 配置文件支持
创建 `config.py`:
```python
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
QUEUE_NAME = 'tweet_queue'
```

## 故障排除

### 常见问题

1. **无法连接到Redis**
   ```
   错误: 无法连接到 Redis，请确保 Redis 服务正在运行
   ```
   解决方案：
   - 检查Redis服务是否启动: `redis-cli ping`
   - 确认端口6379未被占用
   - 检查防火墙设置

2. **队列堵塞**
   如果消费者处理缓慢，可以启动多个消费者实例：
   ```bash
   # 启动多个消费者
   python consumer.py &
   python consumer.py &
   python consumer.py &
   ```

3. **消息格式错误**
   确保生产者发送的JSON格式正确，包含必需的 `message` 字段。

## 性能监控

### 监控队列积压
```bash
# 创建监控脚本
echo 'watch -n 1 "redis-cli LLEN tweet_queue"' > monitor_queue.sh
chmod +x monitor_queue.sh
./monitor_queue.sh
```

### 监控Redis内存使用
```bash
redis-cli info memory
```

## 注意事项

- 这是一个演示项目，生产环境使用需要添加更多错误处理和监控
- 消费者使用无限循环，确保有适当的退出机制
- 建议添加消息重试和死信队列机制
- 考虑使用Redis Streams替代Lists以获得更好的功能特性

## 许可证

本项目仅用于学习和测试目的。 