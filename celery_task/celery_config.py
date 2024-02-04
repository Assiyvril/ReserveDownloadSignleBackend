"""
celery 配置文件  用于 celery 5.3.6 版本
"""
import os

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")

broker_url = f"{REDIS_URL}/14"  # 消息代理
timezone = "Asia/Shanghai"
result_backend = f"{REDIS_URL}/15"  # 结果存储
result_expires = 60 * 60 * 24  # 结果存储过期时间
CELERYD_FORCE_EXECV = True  # 只有当worker执行完任务后,才会告诉MQ,消息被消费，防死锁

accept_content = ['application/json']  # 指定接受的内容类型
task_serializer = 'json'
result_serializer = 'json'
broker_connection_retry_on_startup = True

worker_max_tasks_per_child = 100  # 每个worker最多执行300个任务就会被销毁，可防止内存泄露


worker_hijack_root_logger = False  # 是否启用celery日志
beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

