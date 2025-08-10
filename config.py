import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Twitter API 配置
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
    TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # 应用配置
    QUEUE_NAME = os.getenv('QUEUE_NAME', 'tweet_queue')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_TWEET_LENGTH = int(os.getenv('MAX_TWEET_LENGTH', 280))
    RATE_LIMIT_BUFFER = int(os.getenv('RATE_LIMIT_BUFFER', 5))
    
    @classmethod
    def validate(cls):
        """验证必要的配置是否存在"""
        required_fields = [
            'TWITTER_BEARER_TOKEN',
            'TWITTER_CONSUMER_KEY', 
            'TWITTER_CONSUMER_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必要的配置: {', '.join(missing_fields)}")
        
        return True