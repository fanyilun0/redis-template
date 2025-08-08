# producer_v2.py - 监控服务和内容生成器
# 这个程序负责生成内容并将其发送到队列中。

import redis
import json
import time
import random
import logging
from datetime import datetime
from config import Config

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TweetProducer:
    """推文生产者类"""
    
    def __init__(self):
        """初始化生产者"""
        try:
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
            
        except redis.exceptions.ConnectionError as e:
            logger.error(f"无法连接到 Redis: {e}")
            raise
    
    def generate_monitoring_alert(self) -> dict:
        """生成监控告警事件"""
        services = [
            "数据库服务", "Web服务器", "API网关", "缓存服务", 
            "消息队列", "文件存储", "负载均衡器", "CDN服务"
        ]
        
        alert_types = [
            "服务掉线", "响应时间超时", "CPU使用率过高", 
            "内存不足", "磁盘空间不足", "网络连接异常"
        ]
        
        service_name = random.choice(services)
        alert_type = random.choice(alert_types)
        timestamp = datetime.now()
        
        event = {
            "type": "monitoring_alert",
            "service": service_name,
            "alert_type": alert_type,
            "severity": random.choice(["低", "中", "高", "严重"]),
            "message": f"🚨 警报！{service_name} 检测到 {alert_type}，时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "timestamp": timestamp.isoformat(),
            "metadata": {
                "server_id": f"srv-{random.randint(1000, 9999)}",
                "region": random.choice(["北京", "上海", "广州", "深圳"]),
                "environment": random.choice(["生产", "测试", "开发"])
            }
        }
        return event
    
    def generate_business_update(self) -> dict:
        """生成业务更新事件"""
        updates = [
            "新用户注册量突破1万",
            "系统性能优化完成，响应速度提升30%",
            "新功能上线，用户体验大幅改善",
            "数据备份完成，系统安全性增强",
            "API接口升级，稳定性提升"
        ]
        
        timestamp = datetime.now()
        update_content = random.choice(updates)
        
        event = {
            "type": "business_update",
            "category": "运营更新",
            "message": f"📈 业务更新: {update_content} - {timestamp.strftime('%m月%d日 %H:%M')}",
            "timestamp": timestamp.isoformat(),
            "priority": random.choice(["正常", "重要", "紧急"]),
            "metadata": {
                "department": random.choice(["技术部", "运营部", "产品部"]),
                "author": f"系统管理员{random.randint(1, 10)}"
            }
        }
        return event
    
    def generate_scheduled_content(self) -> dict:
        """生成定时内容"""
        tips = [
            "💡 技巧分享：定期清理系统缓存可以提升应用性能",
            "🔒 安全提醒：请定期更新密码，使用强密码保护账户安全",
            "📊 数据洞察：用户活跃度在上午9-11点和下午2-4点达到峰值",
            "⚡ 性能优化：使用CDN可以显著提升网站访问速度",
            "🛡️ 系统维护：每周定期备份数据，确保业务连续性"
        ]
        
        timestamp = datetime.now()
        tip_content = random.choice(tips)
        
        event = {
            "type": "scheduled_content",
            "category": "定时推送",
            "message": f"{tip_content} #{timestamp.strftime('%Y%m%d')}",
            "timestamp": timestamp.isoformat(),
            "tags": ["技巧", "分享", "运维"],
            "metadata": {
                "content_type": "tip",
                "scheduled": True
            }
        }
        return event
    
    def generate_event(self, event_type: str = None) -> dict:
        """
        根据类型生成事件
        
        Args:
            event_type: 事件类型 ('alert', 'business', 'scheduled', None为随机)
        """
        if event_type is None:
            event_type = random.choice(['alert', 'business', 'scheduled'])
        
        if event_type == 'alert':
            return self.generate_monitoring_alert()
        elif event_type == 'business':
            return self.generate_business_update()
        elif event_type == 'scheduled':
            return self.generate_scheduled_content()
        else:
            return self.generate_monitoring_alert()
    
    def send_to_queue(self, event: dict) -> bool:
        """
        将事件发送到Redis队列
        
        Args:
            event: 事件字典
            
        Returns:
            发送成功返回True，失败返回False
        """
        try:
            # 添加队列元数据
            queue_item = {
                **event,
                "queue_timestamp": time.time(),
                "queue_id": f"msg_{int(time.time() * 1000)}"
            }
            
            # 推送到队列
            result = self.redis_client.lpush(Config.QUEUE_NAME, json.dumps(queue_item, ensure_ascii=False))
            
            if result:
                logger.info(f"✅ 消息已发送到队列 '{Config.QUEUE_NAME}': {event['message'][:100]}...")
                logger.debug(f"完整事件数据: {queue_item}")
                return True
            else:
                logger.error("❌ 发送消息到队列失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 发送消息到队列时发生错误: {e}")
            return False
    
    def get_queue_status(self) -> dict:
        """获取队列状态"""
        try:
            queue_length = self.redis_client.llen(Config.QUEUE_NAME)
            return {
                'queue_name': Config.QUEUE_NAME,
                'queue_length': queue_length,
                'status': 'healthy' if queue_length < 1000 else 'warning',
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
    
    def batch_generate(self, count: int = 5, event_type: str = None) -> int:
        """
        批量生成并发送事件
        
        Args:
            count: 生成数量
            event_type: 事件类型
            
        Returns:
            成功发送的数量
        """
        success_count = 0
        
        for i in range(count):
            try:
                event = self.generate_event(event_type)
                if self.send_to_queue(event):
                    success_count += 1
                    time.sleep(0.5)  # 避免过快发送
                else:
                    logger.warning(f"第 {i+1} 条消息发送失败")
            except Exception as e:
                logger.error(f"生成第 {i+1} 条消息时发生错误: {e}")
        
        logger.info(f"📊 批量生成完成: {success_count}/{count} 条消息发送成功")
        return success_count


def main():
    """主函数"""
    try:
        producer = TweetProducer()
        
        # 显示队列状态
        status = producer.get_queue_status()
        logger.info(f"📋 队列状态: {status}")
        
        # 生成并发送一个事件
        event = producer.generate_event()
        success = producer.send_to_queue(event)
        
        if success:
            logger.info("✅ 事件发送成功!")
        else:
            logger.error("❌ 事件发送失败!")
            
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())