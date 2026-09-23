import os
from dotenv import load_dotenv

load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
SECRET_KEY = os.getenv("SECRET_KEY", "nutriagent-dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nutriagent.db")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# IBM Granite model on Replicate
GRANITE_MODEL = "ibm-granite/granite-3.3-8b-instruct"

# Vision model for food image recognition
VISION_MODEL = "yorickvp/llava-13b:b5f6212d032508382d61ff00469ddda3e32fd8a0867a162dce3b84c1b40665fb"

USE_MOCK = not bool(REPLICATE_API_TOKEN)
