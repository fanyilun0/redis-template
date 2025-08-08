#!/usr/bin/env python3
"""
Twitter Bot 测试脚本
用于测试各个组件的功能
"""

import time
import logging
from producer_v2 import TweetProducer
from consumer_v2 import TweetConsumer
from twitter_client import TwitterClient
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_twitter_connection():
    """测试Twitter API连接"""
    print("\n=== 测试 Twitter API 连接 ===")
    try:
        client = TwitterClient()
        user_info = client.get_user_info()
        
        if user_info:
            print(f"✅ Twitter API 连接正常")
            print(f"👤 用户: @{user_info['username']} ({user_info['name']})")
            print(f"👥 粉丝数: {user_info['followers_count']}")
            print(f"📝 推文数: {user_info['tweet_count']}")
            return True
        else:
            print("❌ 无法获取用户信息")
            return False
            
    except Exception as e:
        print(f"❌ Twitter API 连接失败: {e}")
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n=== 测试 Redis 连接 ===")
    try:
        producer = TweetProducer()
        status = producer.get_queue_status()
        
        print(f"✅ Redis 连接正常")
        print(f"📋 队列名称: {status['queue_name']}")
        print(f"📊 队列长度: {status['queue_length']}")
        return True
        
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return False

def test_message_flow():
    """测试消息流程"""
    print("\n=== 测试消息流程 ===")
    try:
        # 创建生产者和消费者
        producer = TweetProducer()
        consumer = TweetConsumer()
        
        # 清空队列
        initial_status = producer.get_queue_status()
        print(f"📊 初始队列长度: {initial_status['queue_length']}")
        
        # 生成测试消息
        test_event = {
            "type": "test",
            "message": f"🧪 这是一条测试推文 - {time.strftime('%H:%M:%S')}",
            "timestamp": time.time()
        }
        
        # 发送到队列
        print("📤 发送测试消息到队列...")
        success = producer.send_to_queue(test_event)
        
        if not success:
            print("❌ 发送消息到队列失败")
            return False
        
        # 检查队列
        after_send_status = producer.get_queue_status()
        print(f"📊 发送后队列长度: {after_send_status['queue_length']}")
        
        # 处理消息
        print("📥 从队列处理消息...")
        process_success = consumer.process_single_message()
        
        if process_success:
            print("✅ 消息处理成功")
        else:
            print("❌ 消息处理失败")
        
        # 最终队列状态
        final_status = producer.get_queue_status()
        print(f"📊 处理后队列长度: {final_status['queue_length']}")
        
        return process_success
        
    except Exception as e:
        print(f"❌ 消息流程测试失败: {e}")
        return False

def test_batch_generation():
    """测试批量生成"""
    print("\n=== 测试批量生成 ===")
    try:
        producer = TweetProducer()
        
        print("📦 生成3条测试消息...")
        success_count = producer.batch_generate(count=3, event_type='scheduled')
        
        print(f"✅ 成功生成 {success_count}/3 条消息")
        
        status = producer.get_queue_status()
        print(f"📊 当前队列长度: {status['queue_length']}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 批量生成测试失败: {e}")
        return False

def test_twitter_search():
    """测试Twitter搜索功能"""
    print("\n=== 测试 Twitter 搜索 ===")
    try:
        client = TwitterClient()
        
        # 搜索关于Python的推文
        print("🔍 搜索最近的Python相关推文...")
        tweets = client.search_tweets("Python", max_results=5)
        
        if tweets:
            print(f"✅ 找到 {len(tweets)} 条推文")
            for i, tweet in enumerate(tweets[:3], 1):
                print(f"{i}. {tweet['text'][:100]}...")
        else:
            print("ℹ️  未找到相关推文")
        
        return len(tweets) > 0
        
    except Exception as e:
        print(f"❌ Twitter 搜索测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行 Twitter Bot 测试套件")
    print("=" * 50)
    
    tests = [
        ("Twitter API 连接", test_twitter_connection),
        ("Redis 连接", test_redis_connection),
        ("消息流程", test_message_flow),
        ("批量生成", test_batch_generation),
        ("Twitter 搜索", test_twitter_search),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
                
        except Exception as e:
            print(f"❌ {test_name}: 异常 - {e}")
            results.append((test_name, False))
        
        print("-" * 30)
    
    # 总结
    print("\n📊 测试结果总结:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！系统运行正常。")
        return True
    else:
        print("⚠️  有部分测试失败，请检查配置和连接。")
        return False

def interactive_test():
    """交互式测试模式"""
    print("\n🎮 交互式测试模式")
    print("选择要执行的测试:")
    print("1. Twitter API 连接测试")
    print("2. Redis 连接测试")
    print("3. 完整消息流程测试")
    print("4. 批量生成测试")
    print("5. Twitter 搜索测试")
    print("6. 运行所有测试")
    print("0. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (0-6): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                test_twitter_connection()
            elif choice == "2":
                test_redis_connection()
            elif choice == "3":
                test_message_flow()
            elif choice == "4":
                test_batch_generation()
            elif choice == "5":
                test_twitter_search()
            elif choice == "6":
                run_all_tests()
            else:
                print("❌ 无效选择，请输入 0-6")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 执行过程中发生错误: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        run_all_tests()