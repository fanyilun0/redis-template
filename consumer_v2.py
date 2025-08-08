# consumer_v2.py - Twitter 发推机器人
# 这个程序负责从队列中获取内容并发送到Twitter。

import redis
import json
import time
import logging
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config
from twitter_client import TwitterClient

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TweetConsumer:
    """推文消费者类"""
    
    def __init__(self):
        """初始化消费者"""
        self.running = True
        self.twitter_client = None
        self.redis_client = None
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # 初始化Twitter客户端
            self.twitter_client = TwitterClient()
            
            # 连接到Redis
            redis_config = {
                'host': Config.REDIS_HOST,
                'port': Config.REDIS_PORT,
                'db': Config.REDIS_DB,
                'decode_responses': True
            }
            
            if Config.REDIS_PASSWORD:
                redis_config['password'] = Config.REDIS_PASSWORD
            
            self.redis_client = redis.Redis(**redis_config)
            self.redis_client.ping()
            logger.info(f"成功连接到 Redis: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，正在优雅关闭...")
        self.running = False
    
    def process_tweet_task(self, task: dict) -> bool:
        """
        处理推文任务
        
        Args:
            task: 任务字典
            
        Returns:
            处理成功返回True，失败返回False
        """
        try:
            # 提取推文内容
            tweet_content = task.get("message")
            task_type = task.get("type", "unknown")
            
            if not tweet_content:
                logger.error("❌ 任务中没有找到 'message' 字段")
                return False
            
            logger.info(f"📝 处理 {task_type} 类型的推文任务")
            logger.info(f"📄 推文内容: {tweet_content}")
            
            # 发送推文
            result = self.twitter_client.send_tweet(tweet_content)
            
            if result and result.get('success'):
                logger.info(f"✅ 推文发送成功!")
                logger.info(f"🔗 推文链接: {result.get('tweet_url')}")
                
                # 记录成功的推文信息
                self._log_success(task, result)
                return True
            else:
                logger.error(f"❌ 推文发送失败")
                self._log_failure(task, "发送失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 处理推文任务时发生错误: {e}")
            self._log_failure(task, str(e))
            return False
    
    def _log_success(self, task: dict, result: dict):
        """记录成功日志"""
        success_info = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task.get('type'),
            'tweet_id': result.get('tweet_id'),
            'tweet_url': result.get('tweet_url'),
            'content_preview': task.get('message', '')[:100]
        }
        logger.debug(f"📊 成功记录: {success_info}")
    
    def _log_failure(self, task: dict, error_msg: str):
        """记录失败日志"""
        failure_info = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task.get('type'),
            'error': error_msg,
            'content_preview': task.get('message', '')[:100]
        }
        logger.warning(f"📊 失败记录: {failure_info}")
    
    def get_queue_status(self) -> dict:
        """获取队列状态"""
        try:
            queue_length = self.redis_client.llen(Config.QUEUE_NAME)
            return {
                'queue_name': Config.QUEUE_NAME,
                'queue_length': queue_length,
                'status': 'healthy',
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"获取队列状态失败: {e}")
            return {
                'queue_name': Config.QUEUE_NAME,
                'queue_length': -1,
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def run(self):
        """运行消费者主循环"""
        logger.info("🤖 Twitter 发推机器人已启动，正在等待任务...")
        
        # 显示初始状态
        twitter_status = self.twitter_client.get_rate_limit_status()
        queue_status = self.get_queue_status()
        user_info = self.twitter_client.get_user_info()
        
        logger.info(f"📱 Twitter 状态: {twitter_status['status']}")
        logger.info(f"📋 队列状态: {queue_status['queue_length']} 条待处理消息")
        if user_info:
            logger.info(f"👤 认证用户: @{user_info['username']} ({user_info['name']})")
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.running:
            try:
                # 使用阻塞式操作从队列获取任务
                # brpop 会一直等待直到队列中有新消息或超时
                result = self.redis_client.brpop(Config.QUEUE_NAME, timeout=30)
                
                if result is None:
                    # 超时，继续循环
                    logger.debug("⏰ 队列监听超时，继续等待...")
                    continue
                
                source_queue, task_json = result
                task = json.loads(task_json)
                
                logger.info(f"\n🔔 [{datetime.now().strftime('%H:%M:%S')}] 从队列 '{source_queue}' 收到新任务")
                
                # 处理任务
                success = self.process_tweet_task(task)
                
                if success:
                    consecutive_errors = 0  # 重置错误计数
                else:
                    consecutive_errors += 1
                    
                    # 如果连续失败太多次，暂停一下
                    if consecutive_errors >= max_consecutive_errors:
                        logger.warning(f"⚠️  连续 {consecutive_errors} 次处理失败，暂停 60 秒...")
                        time.sleep(60)
                        consecutive_errors = 0
                
                # 任务间隔，避免过于频繁的API调用
                time.sleep(2)
                
            except redis.exceptions.ConnectionError as e:
                logger.error(f"❌ Redis 连接断开，正在尝试重连... ({e})")
                time.sleep(10)
                try:
                    self.redis_client.ping()
                    logger.info("✅ Redis 重连成功")
                    consecutive_errors = 0
                except:
                    consecutive_errors += 1
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ 任务JSON解析失败: {e}")
                consecutive_errors += 1
                
            except KeyboardInterrupt:
                logger.info("🛑 收到中断信号，正在停止...")
                break
                
            except Exception as e:
                logger.error(f"❌ 处理任务时发生未知错误: {e}")
                consecutive_errors += 1
                time.sleep(5)
        
        logger.info("🔚 Twitter 发推机器人已停止")
    
    def process_single_message(self) -> bool:
        """
        处理单条消息（非阻塞模式）
        
        Returns:
            有消息处理返回True，无消息返回False
        """
        try:
            # 非阻塞获取消息
            result = self.redis_client.rpop(Config.QUEUE_NAME)
            
            if result is None:
                return False
            
            task = json.loads(result)
            logger.info(f"🔔 处理单条消息: {task.get('type', 'unknown')}")
            
            return self.process_tweet_task(task)
            
        except Exception as e:
            logger.error(f"❌ 处理单条消息失败: {e}")
            return False


def main():
    """主函数"""
    try:
        consumer = TweetConsumer()
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "single":
                # 处理单条消息模式
                logger.info("🔄 单次处理模式")
                success = consumer.process_single_message()
                if success:
                    logger.info("✅ 消息处理完成")
                    return 0
                else:
                    logger.info("ℹ️  队列中没有待处理消息")
                    return 0
                    
            elif command == "status":
                # 查看状态模式
                logger.info("📊 状态查看模式")
                queue_status = consumer.get_queue_status()
                twitter_status = consumer.twitter_client.get_rate_limit_status()
                user_info = consumer.twitter_client.get_user_info()
                
                print(f"\n=== 系统状态 ===")
                print(f"队列长度: {queue_status['queue_length']} 条消息")
                print(f"Twitter状态: {twitter_status['status']}")
                if user_info:
                    print(f"认证用户: @{user_info['username']} ({user_info['name']})")
                    print(f"粉丝数: {user_info['followers_count']}")
                print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return 0
            
            else:
                print("❌ 无效的命令参数")
                print("使用方法:")
                print("  python consumer_v2.py        # 持续运行模式")
                print("  python consumer_v2.py single # 处理单条消息")
                print("  python consumer_v2.py status # 查看状态")
                return 1
        
        # 默认持续运行模式
        consumer.run()
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())