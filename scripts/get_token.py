import jwt
from datetime import UTC, datetime, timedelta

# Simple token generator
SECRET_KEY = "development_secret_key_replace_in_production"
ALGORITHM = "HS256"

# Create token for Sam
expire = datetime.now(UTC) + timedelta(hours=24)
payload = {
    "sub": "sam123",
    "username": "Sam",
    "exp": int(expire.timestamp()),
    "iat": int(datetime.now(UTC).timestamp()),
}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print("=== SIMPLE LOGIN TOKEN ===")
print("Copy this entire line and paste it in Swagger UI Authorize:")
print(f"Bearer {token}")
print("\nOr just the token part:")
print(token)
