from examples.tests.tests_with_redis_server_need.common import redis_client
import pytest
from redis.exceptions import ConnectionError
from microdrop_utils.redis_manager import RedisHashDictProxy


@pytest.fixture(scope="function")
def redis_dict():
    """
    Fixture to initialize the RedisListHashManager for testing.
    """
    try:
        redis_dict = RedisHashDictProxy(redis_client=redis_client(), hash_name="test_data")
        # Ensure the hash is clean before each test
        redis_dict.clear()
        yield redis_dict
        # Cleanup after test
        redis_dict.clear()
    except ConnectionError:
        pytest.skip("Redis server not running or unreachable.")


def test_set_and_get(redis_dict):
    """
    Test setting and getting items.
    """
    redis_dict["key1"] = ["val1", "val2"]
    assert redis_dict["key1"] == ["val1", "val2"]


def test_set_and_get_tuple(redis_dict):
    """
    Test setting and getting items.
    """
    redis_dict["key1"] = (["val1", "val2"], "home_queue")
    assert ["val1", "val2"], "home_queue" == redis_dict["key1"]


def test_key_existence(redis_dict):
    """
    Test checking key existence.
    """
    redis_dict["key1"] = ["val1", "val2"]
    assert "key1" in redis_dict
    assert "key2" not in redis_dict


def test_delete_key(redis_dict):
    """
    Test deleting a key.
    """
    redis_dict["key1"] = ["val1", "val2"]
    del redis_dict["key1"]
    assert "key1" not in redis_dict


def test_length(redis_dict):
    """
    Test the length of the Redis hash.
    """
    redis_dict["key1"] = ["val1", "val2"]
    redis_dict["key2"] = ["val3", "val4"]
    assert len(redis_dict) == 2


def test_iteration(redis_dict):
    """
    Test iterating over keys.
    """
    redis_dict["key1"] = ["val1", "val2"]
    redis_dict["key2"] = ["val3", "val4"]
    assert "key1" in redis_dict
    assert "key2" in redis_dict.keys()
    assert len(redis_dict) == 2


def test_update_list(redis_dict):
    """
    Test updating a list.
    """
    redis_dict["key1"] = ["val1", "val2"]
    redis_dict["key1"] = ["new_val1", "new_val2"]
    assert redis_dict["key1"] == ["new_val1", "new_val2"]


def test_clear(redis_dict):
    """
    Test clearing all data from the hash.
    """
    redis_dict["key1"] = ["val1", "val2"]
    redis_dict["key2"] = ["val3", "val4"]
    redis_dict.clear()
    assert len(redis_dict) == 0


def test_update_bulk(redis_dict):
    """
    Test updating the hash with a bulk dictionary.
    """
    redis_dict.update({"key1": ["val1", "val2"], "key2": ["val3", "val4"]})
    assert redis_dict["key1"] == ["val1", "val2"]
    assert redis_dict["key2"] == ["val3", "val4"]


def test_invalid_value_type(redis_dict):
    """
    Test that setting a non-list value raises a ValueError.
    """
    with pytest.raises(ValueError):
        redis_dict["key1"] = "not_a_list"


def test_key_not_found(redis_dict):
    """
    Test that accessing a non-existent key raises a KeyError.
    """
    with pytest.raises(KeyError):
        _ = redis_dict["non_existent_key"]
