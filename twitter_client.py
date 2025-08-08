import tweepy
import logging
import time
from typing import Optional, Dict, Any
from config import Config

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterClient:
    """Twitter API 客户端类"""
    
    def __init__(self):
        """初始化Twitter客户端"""
        try:
            # 验证配置
            Config.validate()
            
            # 创建 Twitter API v2 客户端
            self.client = tweepy.Client(
                bearer_token=Config.TWITTER_BEARER_TOKEN,
                consumer_key=Config.TWITTER_CONSUMER_KEY,
                consumer_secret=Config.TWITTER_CONSUMER_SECRET,
                access_token=Config.TWITTER_ACCESS_TOKEN,
                access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True  # 自动处理速率限制
            )
            
            # 验证认证
            self._verify_credentials()
            logger.info("Twitter API 客户端初始化成功")
            
        except Exception as e:
            logger.error(f"Twitter API 客户端初始化失败: {e}")
            raise
    
    def _verify_credentials(self):
        """验证Twitter API凭据"""
        try:
            user = self.client.get_me()
            if user.data:
                logger.info(f"已认证用户: @{user.data.username} ({user.data.name})")
                return True
            else:
                raise Exception("无法获取用户信息")
        except Exception as e:
            logger.error(f"Twitter API 凭据验证失败: {e}")
            raise
    
    def send_tweet(self, content: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        发送推文
        
        Args:
            content: 推文内容
            **kwargs: 其他参数，如 in_reply_to_tweet_id, media_ids 等
            
        Returns:
            发送成功的推文信息，失败时返回 None
        """
        try:
            # 验证推文长度
            if len(content) > Config.MAX_TWEET_LENGTH:
                logger.warning(f"推文内容超过 {Config.MAX_TWEET_LENGTH} 字符限制，当前长度: {len(content)}")
                content = content[:Config.MAX_TWEET_LENGTH-3] + "..."
                logger.info(f"推文已截断为: {content}")
            
            # 发送推文
            logger.info(f"正在发送推文: {content[:50]}...")
            response = self.client.create_tweet(text=content, **kwargs)
            
            if response.data:
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                logger.info(f"推文发送成功! Tweet ID: {tweet_id}")
                logger.info(f"推文链接: {tweet_url}")
                
                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url,
                    'content': content,
                    'timestamp': time.time()
                }
            else:
                logger.error("推文发送失败: 未收到有效响应")
                return None
                
        except tweepy.TooManyRequests as e:
            logger.warning(f"达到速率限制，等待重试... {e}")
            time.sleep(Config.RATE_LIMIT_BUFFER * 60)  # 等待几分钟后重试
            return self.send_tweet(content, **kwargs)
            
        except tweepy.Forbidden as e:
            logger.error(f"权限被拒绝，可能是内容违规或账号限制: {e}")
            return None
            
        except tweepy.BadRequest as e:
            logger.error(f"请求格式错误: {e}")
            return None
            
        except Exception as e:
            logger.error(f"发送推文时发生未知错误: {e}")
            return None
    
    def get_user_info(self, username: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            username: 用户名 (不包含@)
            user_id: 用户ID
            
        Returns:
            用户信息字典，失败时返回 None
        """
        try:
            if username:
                user = self.client.get_user(username=username)
            elif user_id:
                user = self.client.get_user(id=user_id)
            else:
                # 获取当前认证用户信息
                user = self.client.get_me()
            
            if user.data:
                return {
                    'id': user.data.id,
                    'username': user.data.username,
                    'name': user.data.name,
                    'description': getattr(user.data, 'description', ''),
                    'followers_count': getattr(user.data, 'public_metrics', {}).get('followers_count', 0),
                    'following_count': getattr(user.data, 'public_metrics', {}).get('following_count', 0),
                    'tweet_count': getattr(user.data, 'public_metrics', {}).get('tweet_count', 0)
                }
            else:
                logger.error("无法获取用户信息")
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def search_tweets(self, query: str, max_results: int = 10) -> list:
        """
        搜索推文
        
        Args:
            query: 搜索查询
            max_results: 最大结果数 (1-100)
            
        Returns:
            推文列表
        """
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )
            
            if tweets.data:
                return [
                    {
                        'id': tweet.id,
                        'text': tweet.text,
                        'author_id': tweet.author_id,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                        'public_metrics': getattr(tweet, 'public_metrics', {})
                    }
                    for tweet in tweets.data
                ]
            else:
                logger.info(f"未找到匹配查询 '{query}' 的推文")
                return []
                
        except Exception as e:
            logger.error(f"搜索推文失败: {e}")
            return []
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        获取当前的速率限制状态
        
        Returns:
            速率限制信息字典
        """
        try:
            # 注意: Twitter API v2 不直接提供速率限制状态端点
            # 这里我们可以通过发送一个简单的请求来检查状态
            user = self.client.get_me()
            if user:
                return {
                    'status': 'ok',
                    'message': '连接正常',
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'error',
                    'message': '无法连接到Twitter API',
                    'timestamp': time.time()
                }
        except tweepy.TooManyRequests as e:
            return {
                'status': 'rate_limited',
                'message': f'达到速率限制: {e}',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'检查状态失败: {e}',
                'timestamp': time.time()
            }