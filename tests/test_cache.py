from redis_cache import RedisCache


class TestCache:
    def test_save_get_value(self):
        cache = RedisCache()
        key = "x1:y1"
        if cache.check_cache(key):
            cache.redis.delete(key)
        assert not cache.check_cache(key)
        test_data_dict = {"key1": "value1", "key2": "value2"}
        cache.save_to_cache(key, test_data_dict)

        assert cache.check_cache(key)

        test_value = cache.get_from_cache(key)

        assert test_value["key1"] == "value1"
        assert test_value["key1"] == "value1"

    def test_check_value(self):
        cache = RedisCache()
        key = "x1"
        if cache.check_cache(key):
            cache.redis.delete(key)
        assert not cache.check_cache(key)
        test_data_dict = {"key1": "value1", "key2": "value2"}
        cache.save_to_cache(key, test_data_dict)

        assert cache.check_cache(key)
