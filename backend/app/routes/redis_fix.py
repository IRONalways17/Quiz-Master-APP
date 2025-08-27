# Temporary fix for Redis deployment issue
# Disable Redis caching to get the app running

def get_#redis_client():
    return None
