import redis
import os


REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL is None:
    print("Make sure REDIS_URL envVar is setup !")
    exit(1)

def find_sets_with_member(redis_connection, document_id):
    matched_sets = []
    # Use scan_iter with a match pattern to find potential set keys
    for key in redis_connection.scan_iter(match="SET_*", type="set"):
        if redis_connection.sismember(key, document_id):
            matched_sets.append(key.decode())
    
    # Removing the SET_ from the pattern
    matched_sets = list(map(lambda x : x[4:], matched_sets))
    return matched_sets


def create_redis_connection_pool():
    connectionPool = redis.ConnectionPool.from_url(
        url=REDIS_URL,
    )
    connectionPool.max_connections = 10
    return connectionPool


pool = create_redis_connection_pool()
