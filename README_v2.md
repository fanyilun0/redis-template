# Redis + Twitter API v2 智能推文机器人

这是一个基于Redis消息队列和Twitter API v2的现代化推文机器人系统，支持监控告警、业务更新和定时内容的自动化推送。

## 🌟 功能特点

### 核心功能
- **🤖 智能推文机器人**: 使用 Twitter API v2 自动发送推文
- **📊 多类型内容生成**: 支持监控告警、业务更新、定时内容
- **⚡ Redis 消息队列**: 高性能的异步消息处理
- **🔄 优雅的错误处理**: 自动重试和速率限制处理
- **📈 实时监控**: 队列状态和系统健康检查

### 技术特色
- **Twitter API v2**: 使用最新的官方API，支持OAuth 2.0
- **环境配置管理**: 使用 `.env` 文件安全管理密钥
- **日志系统**: 完整的日志记录和错误追踪
- **批量处理**: 支持单条和批量消息处理
- **信号处理**: 优雅的启动和停止机制

## 📁 项目结构

```
redis/
├── 📦 核心文件 (V2升级版)
│   ├── producer_v2.py      # 升级版生产者
│   ├── consumer_v2.py      # 升级版消费者  
│   ├── twitter_client.py   # Twitter API v2 客户端
│   ├── config.py          # 配置管理
│   └── test_bot.py        # 测试脚本
├── 📋 配置文件
│   ├── requirements.txt   # Python依赖
│   ├── .env.example       # 环境变量模板
│   └── README_v2.md       # 使用文档
├── 📜 原始文件 (保留)
│   ├── producer.py        # 原始生产者
│   ├── consumer.py        # 原始消费者
│   └── README.md          # 原始文档
└── 🔧 系统文件
    ├── .git/              # Git仓库
    ├── .venv/             # Python虚拟环境
    └── .gitignore         # Git忽略文件
```

## 🚀 快速开始

### 1. 环境要求

- **Python 3.7+**
- **Redis 服务器**
- **Twitter Developer 账号**

### 2. 安装 Redis

**Windows (Docker):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**macOS:**
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

### 3. 申请 Twitter Developer 账号

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 申请开发者账号 (现在可以即时获得基础访问权限)
3. 创建一个新的 App
4. 获取以下凭据:
   - **Bearer Token**
   - **Consumer Key** 和 **Consumer Secret**
   - **Access Token** 和 **Access Token Secret**

### 4. 项目设置

**安装 Python 依赖:**
```bash
pip install -r requirements.txt
```

**配置环境变量:**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Twitter API 凭据
```

**.env 文件配置示例:**
```env
# Twitter API 配置
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_CONSUMER_KEY=your_consumer_key_here
TWITTER_CONSUMER_SECRET=your_consumer_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 应用配置
QUEUE_NAME=tweet_queue
LOG_LEVEL=INFO
MAX_TWEET_LENGTH=280
RATE_LIMIT_BUFFER=5
```

### 5. 系统测试

**运行完整测试:**
```bash
python test_bot.py
```

**交互式测试:**
```bash
python test_bot.py interactive
```

**测试输出示例:**
```
🧪 开始运行 Twitter Bot 测试套件
==================================================

=== 测试 Twitter API 连接 ===
✅ Twitter API 连接正常
👤 用户: @your_username (Your Name)
👥 粉丝数: 123
📝 推文数: 456

=== 测试 Redis 连接 ===
✅ Redis 连接正常
📋 队列名称: tweet_queue
📊 队列长度: 0

🎯 总计: 5/5 项测试通过
🎉 所有测试都通过了！系统运行正常。
```

## 🎯 使用指南

### 生产者 (Producer) - 内容生成

**生成单条消息:**
```bash
python producer_v2.py
```

**批量生成消息:**
```python
from producer_v2 import TweetProducer

producer = TweetProducer()

# 生成 5 条监控告警
producer.batch_generate(count=5, event_type='alert')

# 生成 3 条业务更新  
producer.batch_generate(count=3, event_type='business')

# 生成随机类型内容
producer.batch_generate(count=10)
```

**支持的内容类型:**
- `alert`: 监控告警 (🚨 服务器问题、性能警报等)
- `business`: 业务更新 (📈 运营数据、功能上线等)  
- `scheduled`: 定时内容 (💡 技巧分享、安全提醒等)

### 消费者 (Consumer) - 推文机器人

**持续运行模式:**
```bash
python consumer_v2.py
```

**处理单条消息:**
```bash
python consumer_v2.py single
```

**查看系统状态:**
```bash
python consumer_v2.py status
```

**运行输出示例:**
```
🤖 Twitter 发推机器人已启动，正在等待任务...
📱 Twitter 状态: ok
📋 队列状态: 3 条待处理消息  
👤 认证用户: @your_bot (Bot Name)

🔔 [14:30:25] 从队列 'tweet_queue' 收到新任务
📝 处理 monitoring_alert 类型的推文任务
📄 推文内容: 🚨 警报！数据库服务 检测到 响应时间超时，时间: 2024-01-15 14:30:25
✅ 推文发送成功!
🔗 推文链接: https://twitter.com/user/status/1234567890
```

## 📊 监控和管理

### 队列状态监控

**Python 脚本方式:**
```python
from producer_v2 import TweetProducer

producer = TweetProducer()
status = producer.get_queue_status()
print(f"队列长度: {status['queue_length']}")
```

**Redis CLI 方式:**
```bash
redis-cli

# 查看队列长度
LLEN tweet_queue

# 查看队列内容 (不移除)
LRANGE tweet_queue 0 -1

# 清空队列
DEL tweet_queue
```

### 日志管理

日志级别可通过环境变量 `LOG_LEVEL` 设置:
- `DEBUG`: 详细调试信息
- `INFO`: 常规信息 (默认)
- `WARNING`: 警告信息
- `ERROR`: 错误信息

## 🔧 高级配置

### Twitter API 速率限制

系统自动处理 Twitter API 的速率限制:

| 功能 | 免费版限制 | 基础版限制 | 专业版限制 |
|------|------------|------------|------------|
| 发推文 | 17条/24小时 | 100条/24小时 | 10,000条/24小时 |
| 搜索推文 | 1次/15分钟 | 60次/15分钟 | 300次/15分钟 |
| 用户查询 | 1次/24小时 | 500次/24小时 | 无限制 |

### 自定义内容生成

**扩展生产者类:**
```python
from producer_v2 import TweetProducer

class CustomProducer(TweetProducer):
    def generate_custom_content(self):
        return {
            "type": "custom",
            "message": "你的自定义内容",
            "timestamp": time.time(),
            "metadata": {"source": "custom_generator"}
        }

# 使用自定义生成器
producer = CustomProducer()
event = producer.generate_custom_content()
producer.send_to_queue(event)
```

### 多环境部署

**开发环境:**
```env
LOG_LEVEL=DEBUG
REDIS_HOST=localhost
```

**生产环境:**
```env  
LOG_LEVEL=INFO
REDIS_HOST=prod-redis.example.com
REDIS_PASSWORD=your_redis_password
```

## 🛠️ 故障排除

### 常见问题

**1. Twitter API 认证失败**
```
❌ Twitter API 客户端初始化失败: 401 Unauthorized
```
**解决方案:**
- 检查 `.env` 文件中的 Twitter API 凭据
- 确保 Access Token 权限设置为 "Read and Write"
- 验证 App 的认证设置

**2. Redis 连接失败**
```
❌ 无法连接到 Redis: Connection refused
```
**解决方案:**
- 确保 Redis 服务正在运行: `redis-cli ping`
- 检查 Redis 配置: 主机、端口、密码
- 防火墙和网络连接检查

**3. 队列处理缓慢**
**解决方案:**
- 启动多个消费者实例
- 调整 `RATE_LIMIT_BUFFER` 参数
- 监控 Twitter API 配额使用情况

**4. 推文内容被截断**
```
⚠️  推文内容超过 280 字符限制，当前长度: 320
```
**解决方案:**
- 系统会自动截断并添加 "..."
- 修改生成器逻辑控制内容长度
- 使用推文串 (Thread) 发送长内容

### 日志调试

**启用详细日志:**
```bash
export LOG_LEVEL=DEBUG
python consumer_v2.py
```

**查看特定错误:**
```bash
python consumer_v2.py 2>&1 | grep "ERROR"
```

## 🚀 部署建议

### 系统服务部署 (Linux)

**创建 systemd 服务:**
```bash
sudo nano /etc/systemd/system/twitter-bot.service
```

```ini
[Unit]
Description=Twitter Bot Consumer
After=network.target redis.service

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/redis
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python consumer_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务:**
```bash
sudo systemctl enable twitter-bot
sudo systemctl start twitter-bot
sudo systemctl status twitter-bot
```

### Docker 部署

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "consumer_v2.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  twitter-bot:
    build: .
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
    env_file:
      - .env
```

## 📈 性能优化

### 批量处理优化

```python
# 批量生成和处理
producer = TweetProducer()
consumer = TweetConsumer()

# 批量生成 50 条消息
producer.batch_generate(50)

# 批量处理所有消息
while consumer.process_single_message():
    time.sleep(1)  # 控制处理速度
```

### 并发处理

```bash
# 启动多个消费者实例
python consumer_v2.py &
python consumer_v2.py &
python consumer_v2.py &
```

## 🔒 安全建议

1. **环境变量管理**: 永远不要将 `.env` 文件提交到版本控制
2. **API 密钥轮换**: 定期更新 Twitter API 凭据
3. **网络安全**: 在生产环境中使用 TLS/SSL 连接 Redis
4. **访问控制**: 限制 Redis 访问权限
5. **日志安全**: 确保日志中不包含敏感信息

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 报告问题
- 使用 GitHub Issues 报告 bug
- 提供详细的错误信息和复现步骤

### 功能请求  
- 描述新功能的使用场景
- 提供设计草图或示例代码

### 代码贡献
1. Fork 项目
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -m "Add new feature"`
4. 推送分支: `git push origin feature/new-feature`
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与帮助

- **文档**: [项目 Wiki](https://github.com/your-repo/wiki)
- **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

## 🔄 版本对比

### V2版本 (推荐使用)
- `producer_v2.py` - 升级版生产者
- `consumer_v2.py` - 升级版消费者  
- `twitter_client.py` - Twitter API v2 客户端
- `config.py` - 配置管理
- `test_bot.py` - 完整测试套件

### V1版本 (原始版本)
- `producer.py` - 原始生产者
- `consumer.py` - 原始消费者

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

**🔔 关注项目动态，获取最新更新和功能！**