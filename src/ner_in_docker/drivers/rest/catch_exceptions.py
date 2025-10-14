from functools import wraps
from fastapi import HTTPException
from requests import HTTPError
import traceback


def catch_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPError:
            raise HTTPException(status_code=400, detail="Unprocessable text or PDF file")
        except Exception as e:
            print(f"error {e}")
            traceback.print_exc()
            raise HTTPException(status_code=422, detail="Error see traceback")

    return wrapper
