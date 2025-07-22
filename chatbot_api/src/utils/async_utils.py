
import asyncio

def async_retry(max_retries=3, delay=1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for i in range(1,max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    print(f"async_retry - Error: {e}")
                    await asyncio.sleep(delay)
            # return None
            raise ValueError(f"Failed after {max_retries} retries attempts.")
        return wrapper
    return decorator