# test_redis.py - Redis连接测试脚本
# 用于验证Redis服务是否正常运行并可以通过Python连接

import redis
import sys

def test_redis_connection():
    """
    测试Redis连接功能
    包括：连接测试、读写测试、数据类型测试
    """
    print("🔍 开始测试Redis连接...")
    
    try:
        # 创建Redis连接
        # host: Redis服务器地址（本地为localhost）
        # port: Redis端口（默认6379）
        # db: 数据库编号（0-15，默认0）
        # decode_responses: 自动解码响应为字符串
        r = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True
        )
        
        # 1. 测试基本连接
        print("\n📡 测试1：基本连接测试")
        response = r.ping()
        if response:
            print("✅ Redis连接成功！服务器响应: PONG")
        else:
            print("❌ Redis连接失败")
            return False
            
        # 2. 测试字符串操作
        print("\n📝 测试2：字符串读写测试")
        test_key = 'mininutriscan:test'
        test_value = 'Hello MiniNutriScan!'
        
        # 写入数据
        r.set(test_key, test_value)
        print(f"✅ 写入数据: {test_key} = {test_value}")
        
        # 读取数据
        retrieved_value = r.get(test_key)
        print(f"✅ 读取数据: {test_key} = {retrieved_value}")
        
        # 验证数据一致性
        if retrieved_value == test_value:
            print("✅ 数据一致性验证通过")
        else:
            print("❌ 数据一致性验证失败")
            return False
            
        # 3. 测试过期时间
        print("\n⏰ 测试3：过期时间测试")
        expire_key = 'mininutriscan:expire_test'
        r.setex(expire_key, 5, 'This will expire in 5 seconds')
        ttl = r.ttl(expire_key)
        print(f"✅ 设置过期键: {expire_key}, 剩余时间: {ttl}秒")
        
        # 4. 测试哈希操作
        print("\n🗂️ 测试4：哈希数据结构测试")
        hash_key = 'mininutriscan:user:1'
        user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'created_at': '2024-08-10'
        }
        
        # 写入哈希数据
        r.hmset(hash_key, user_data)
        print(f"✅ 写入哈希数据: {hash_key}")
        
        # 读取哈希数据
        retrieved_hash = r.hgetall(hash_key)
        print(f"✅ 读取哈希数据: {retrieved_hash}")
        
        # 5. 测试列表操作
        print("\n📋 测试5：列表数据结构测试")
        list_key = 'mininutriscan:food_history'
        foods = ['苹果', '香蕉', '橙子', '葡萄']
        
        # 清空可能存在的列表
        r.delete(list_key)
        
        # 添加列表元素
        for food in foods:
            r.lpush(list_key, food)
        print(f"✅ 添加列表数据: {foods}")
        
        # 读取列表数据
        retrieved_list = r.lrange(list_key, 0, -1)
        print(f"✅ 读取列表数据: {retrieved_list}")
        
        # 6. 清理测试数据
        print("\n🧹 清理测试数据")
        cleanup_keys = [test_key, hash_key, list_key]
        for key in cleanup_keys:
            if r.exists(key):
                r.delete(key)
                print(f"✅ 删除测试键: {key}")
        
        # 7. 获取Redis信息
        print("\n📊 Redis服务器信息")
        info = r.info()
        print(f"✅ Redis版本: {info.get('redis_version', 'Unknown')}")
        print(f"✅ 已用内存: {info.get('used_memory_human', 'Unknown')}")
        print(f"✅ 连接客户端数: {info.get('connected_clients', 'Unknown')}")
        print(f"✅ 运行时间: {info.get('uptime_in_seconds', 'Unknown')}秒")
        
        print("\n🎉 所有Redis测试通过！")
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis连接错误: {e}")
        print("💡 解决方案:")
        print("   1. 确保Redis服务正在运行")
        print("   2. 检查Redis端口6379是否可用")
        print("   3. 确认防火墙设置")
        print("   4. 重启Redis服务")
        return False
        
    except redis.ResponseError as e:
        print(f"❌ Redis响应错误: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def check_redis_requirements():
    """
    检查Redis相关的Python包是否已安装
    """
    try:
        import redis
        print(f"✅ Redis Python包已安装，版本: {redis.__version__}")
        return True
    except ImportError:
        print("❌ Redis Python包未安装")
        print("💡 请运行: pip install redis")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 MiniNutriScan Redis 连接测试")
    print("=" * 50)
    
    # 检查依赖
    if not check_redis_requirements():
        sys.exit(1)
    
    # 运行测试
    success = test_redis_connection()
    
    if success:
        print("\n🎯 Redis环境配置完成！")
        print("📝 下一步可以继续配置AI服务")
    else:
        print("\n❌ Redis测试失败，请检查配置")
        sys.exit(1)