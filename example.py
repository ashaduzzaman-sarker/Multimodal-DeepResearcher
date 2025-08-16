import os
import redis
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
r = redis.from_url(redis_url)

# Test connection
r.set("mykey", "Hello Redis!")
print(r.get("mykey").decode())
