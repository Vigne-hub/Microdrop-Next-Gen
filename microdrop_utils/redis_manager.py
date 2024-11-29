import json
from traits.api import HasTraits, Instance, Str


class RedisHashDictProxy(HasTraits):

    redis_client = Instance('redis.StrictRedis')
    hash_name = Str("routing_info")

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
        keys = []

        # check if keys need to be decoded:
        for key in self.redis_client.hkeys(self.hash_name):
            if isinstance(key, bytes):
                key = key.decode()

            keys.append(key)

        return keys

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
    from microdrop_utils.broker_server_helpers import redis_server_context
    from dramatiq import get_broker

    with redis_server_context():
        client = get_broker().client
        # Initialize manager
        redis_dict = RedisHashDictProxy(redis_client=client, hash_name="example_data")

        # Set items
        redis_dict["key1"] = ["val1", "val2"]
        redis_dict["key2"] = ["val3", "val4"]

        # Get items
        print("Get 'key1':", redis_dict["key1"])  # ['val1', 'val2']

        # Check existence
        print("'key1' in manager:", "key1" in redis_dict)  # True

        # Iterate over keys
        print("Keys:", list(redis_dict))  # ['key1', 'key2']

        # Length
        print("Length:", len(redis_dict))  # 2

        # Delete a key
        del redis_dict["key2"]
        print("After deletion:", list(redis_dict))  # ['key1']

        # Update with a dictionary
        redis_dict.update({"key3": ["val5", "val6"], "key4": ["val7"]})
        print("Updated items:", list(redis_dict.items()))  # [('key1', [...]), ('key3', [...]), ...]

        # Clear all data
        redis_dict.clear()
        print("After clearing:", list(redis_dict))  # []
