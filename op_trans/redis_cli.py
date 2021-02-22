import redis

class RedisCli:
    instance = None

    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = redis.Redis(host='localhost', port=6379, db=0)
        return cls.instance