from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, PyJWTError

from app.core.settings import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials: Bearer token missing.",
        )

    settings = get_settings()
    decode_kwargs = {
        "algorithms": [settings.jwt_algorithm],
        "options": {
            "verify_signature": True,
            "verify_aud": settings.jwt_audience is not None,
            "verify_iss": settings.jwt_issuer is not None,
            "verify_exp": True,
        },
    }
    if settings.jwt_audience is not None:
        decode_kwargs["audience"] = settings.jwt_audience
    if settings.jwt_issuer is not None:
        decode_kwargs["issuer"] = settings.jwt_issuer

    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, **decode_kwargs)
    except ExpiredSignatureError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.") from error
    except (InvalidAudienceError, InvalidIssuerError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims.") from error
    except PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from error

    user_id = payload.get("user_id") or payload.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token user id missing.")
    return user_id
