"""
autotwitter.py - Alpha 事件专用消费者

功能:
- 从 Redis 队列消费结构化 Alpha 事件(JSON)
- 事件包含: 链/代币名与符号/数量/合约/浏览器 等字段
- 使用模板格式化推文并通过 twitter_client 发送

事件JSON字段规范 (与 alpha.json 对齐):
{
  "type": "alpha_new_token",
  "chain": str,
  "address": str,
  "name": str,
  "symbol": str,
  "amount": int | float | str,
  "contract": str,
  "explorer": str,
  "threshold": int | float,
  "detected_at": str
}
"""

import os
import json
import time
import signal
import logging
from typing import Dict, Any

import redis

from config import Config
from twitter_client import TwitterClient


logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'alpha_template.txt')


def load_template() -> str:
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def format_amount(value: Any) -> str:
    try:
        # 尝试数值格式化，千分位
        num = float(value)
        if abs(num) >= 1000:
            return f"{num:,.0f}"
        # 保留最多4位小数
        return (f"{num:.4f}".rstrip('0').rstrip('.'))
    except Exception:
        return str(value)


def build_tweet_content(event: Dict[str, Any]) -> str:
    template = load_template()
    # 允许缺省字段安全回退
    data = {
        'chain': event.get('chain', 'Unknown Chain'),
        'address': event.get('address', 'N/A'),
        'name': event.get('name', 'Unknown'),
        'symbol': event.get('symbol', '?'),
        'amount': format_amount(event.get('amount', '0')),
        'contract': event.get('contract', 'N/A'),
        'explorer': event.get('explorer', ''),
        'detected_at': event.get('detected_at', ''),
    }
    return template.format(**data)

class AlphaConsumer:
    def __init__(self):
        self.running = True
        # 初始化 Twitter
        self.twitter = TwitterClient()
        self.twitterSending = True  # 启用推文发送
        # 初始化 Redis
        redis_config = {
            'host': Config.REDIS_HOST,
            'port': Config.REDIS_PORT,
            'db': Config.REDIS_DB,
            'decode_responses': True,
        }
        if Config.REDIS_PASSWORD:
            redis_config['password'] = Config.REDIS_PASSWORD
        self.rds = redis.Redis(**redis_config)
        self.rds.ping()
        logger.info(f"连接 Redis 成功: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        # 信号
        signal.signal(signal.SIGINT, self._signal)
        signal.signal(signal.SIGTERM, self._signal)

    def _signal(self, signum, frame):
        logger.info(f"收到信号 {signum}，准备退出...")
        self.running = False

    def validate_event(self, event: Dict[str, Any]) -> bool:
        required = ['type', 'chain', 'name', 'symbol', 'amount', 'contract', 'explorer']
        for key in required:
            if key not in event or event[key] in (None, ''):
                logger.error(f"事件缺少必要字段: {key}")
                return False
        if str(event.get('type')) != 'alpha_new_token':
            logger.warning(f"事件类型不是 alpha_new_token: {event.get('type')}")
        return True

    def process_event(self, event: Dict[str, Any]) -> bool:
        if not self.validate_event(event):
            return False
        content = build_tweet_content(event)
        if self.twitterSending:
            result = self.twitter.send_tweet(content)
            return bool(result and result.get('success'))
        else:
            # 如果不发送推文，仅记录内容并返回成功
            logger.info(f"推文内容预览（未发送）: {content}")
            return True

    def run(self):
        logger.info("Alpha 消费者启动，监听队列: %s", Config.QUEUE_NAME)
        while self.running:
            try:
                item = self.rds.brpop(Config.QUEUE_NAME, timeout=30)
                if item is None:
                    continue
                _, raw = item
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    logger.error("队列消息不是合法JSON，已跳过")
                    continue
                # 仅处理 Alpha 事件；其他类型交给 v2 消费者
                if event.get('type') != 'alpha_new_token':
                    logger.debug("非 alpha 事件，跳过: %s", event.get('type'))
                    continue
                ok = self.process_event(event)
                if ok:
                    logger.info("✅ 推文发送成功")
                else:
                    logger.error("❌ 推文发送失败")
                time.sleep(2)
            except redis.exceptions.ConnectionError as e:
                logger.error(f"Redis 连接中断: {e}")
                time.sleep(5)
                try:
                    self.rds.ping()
                    logger.info("Redis 重连成功")
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"处理循环异常: {e}")
                time.sleep(2)


def main():
    consumer = AlphaConsumer()
    consumer.run()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


