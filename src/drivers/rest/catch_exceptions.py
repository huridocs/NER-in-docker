from functools import wraps
from fastapi import HTTPException
from requests import HTTPError


def catch_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if kwargs["text"] is None and kwargs["file"] is None:
                raise ValueError
            return await func(*args, **kwargs)
        except ValueError:
            raise HTTPException(status_code=400, detail="No files or text provided")
        except HTTPError:
            raise HTTPException(status_code=400, detail="Unprocessable PDF file")
        except Exception as e:
            print(f"error {e}")
            raise HTTPException(status_code=422, detail="Error see traceback")

    return wrapper
