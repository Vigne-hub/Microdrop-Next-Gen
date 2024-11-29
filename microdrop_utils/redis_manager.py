import redis
import json


class RedisHashDictProxy:
    def __init__(self, redis_host='localhost', redis_port=6379, hash_name="my_data"):
        """
        Initializes the Redis connection and hash name.
        """
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        self.hash_name = hash_name

    # Magic methods to make the class behave like a dictionary
    def __getitem__(self, key):
        """
        Retrieves the list associated with the key.
        """
        value = self.redis_client.hget(self.hash_name, key)
        if value is None:
            raise KeyError(f"Key '{key}' does not exist.")
        return json.loads(value)

    def __setitem__(self, key, value):
        """
        Sets the list for a given key.
        """
        if not isinstance(value, list):
            raise ValueError("Value must be a list.")
        self.redis_client.hset(self.hash_name, key, json.dumps(value))

    def __delitem__(self, key):
        """
        Deletes a key from the Redis hash.
        """
        if not self.redis_client.hdel(self.hash_name, key):
            raise KeyError(f"Key '{key}' does not exist.")

    def __contains__(self, key):
        """
        Checks if a key exists in the Redis hash.
        """
        return self.redis_client.hexists(self.hash_name, key)

    def __len__(self):
        """
        Returns the number of keys in the Redis hash.
        """
        return self.redis_client.hlen(self.hash_name)

    def __iter__(self):
        """
        Returns an iterator over the keys in the Redis hash.
        """
        return iter(self.redis_client.hkeys(self.hash_name))

    def __repr__(self):
        """
        Returns a string representation of the Redis hash.
        """
        return str({k: json.loads(v) for k, v in self.redis_client.hgetall(self.hash_name).items()})

    # Additional dictionary-like methods
    def keys(self):
        """
        Returns the keys in the Redis hash.
        """
        return self.redis_client.hkeys(self.hash_name)

    def values(self):
        """
        Returns the values (as lists) in the Redis hash.
        """
        return [json.loads(v) for v in self.redis_client.hvals(self.hash_name)]

    def items(self):
        """
        Returns the key-value pairs (keys and lists) in the Redis hash.
        """
        return ((k, json.loads(v)) for k, v in self.redis_client.hgetall(self.hash_name).items())

    def clear(self):
        """
        Deletes all keys in the Redis hash.
        """
        self.redis_client.delete(self.hash_name)

    def get(self, key, default=None):
        """
        Gets a value by key, returning a default if the key does not exist.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, data):
        """
        Updates the Redis hash with the provided dictionary of lists.
        """
        if not all(isinstance(v, list) for v in data.values()):
            raise ValueError("All values must be lists.")
        self.redis_client.hmset(self.hash_name, mapping={k: json.dumps(v) for k, v in data.items()})


# Example usage
if __name__ == "__main__":
    # Initialize manager
    manager = RedisHashDictProxy(hash_name="example_data")

    # Set items
    manager["key1"] = ["val1", "val2"]
    manager["key2"] = ["val3", "val4"]

    # Get items
    print("Get 'key1':", manager["key1"])  # ['val1', 'val2']

    # Check existence
    print("'key1' in manager:", "key1" in manager)  # True

    # Iterate over keys
    print("Keys:", list(manager))  # ['key1', 'key2']

    # Length
    print("Length:", len(manager))  # 2

    # Delete a key
    del manager["key2"]
    print("After deletion:", list(manager))  # ['key1']

    # Update with a dictionary
    manager.update({"key3": ["val5", "val6"], "key4": ["val7"]})
    print("Updated items:", list(manager.items()))  # [('key1', [...]), ('key3', [...]), ...]

    # Clear all data
    manager.clear()
    print("After clearing:", list(manager))  # []
