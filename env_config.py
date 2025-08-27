import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI Configuration
class Settings:
    # Django Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "django-secret-1aZ3Qm9YpQ6uZr0F8dV7xK2wB5eN4tH9sJ3uC1pL7qT0mR6yV2aW")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    ALLOWED_HOSTS: str = os.getenv("ALLOWED_HOSTS", "*")
    
    # VAPT API Settings
    VAPT_API_KEY: str = os.getenv("VAPT_API_KEY", "vapt-key-u3JkN9qX4sW8yZ2tL6aP0vB3mH7cD1rF5xG9kT2nV4pS8qL0wE3")
    
    # Celery Settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_ALWAYS_EAGER: bool = os.getenv("CELERY_ALWAYS_EAGER", "true").lower() == "true"
    CELERY_EAGER_PROPAGATES: bool = os.getenv("CELERY_EAGER_PROPAGATES", "false").lower() == "true"
    
    # ZAP Settings
    ZAP_HTTP: str = os.getenv("ZAP_HTTP", "http://127.0.0.1:8080")
    ZAP_HTTPS: str = os.getenv("ZAP_HTTPS", "http://127.0.0.1:8080")
    
    # CORS Settings
    CORS_ALLOW_ALL: bool = os.getenv("CORS_ALLOW_ALL", "true").lower() == "true"
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:8001")
    
    # Startup Scan Settings
    STARTUP_SCAN_URL: str = os.getenv("STARTUP_SCAN_URL", "")
    STARTUP_SCAN_ENGINE: str = os.getenv("STARTUP_SCAN_ENGINE", "zap")
    
    # FastAPI Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8001"))

# Create settings instance
settings = Settings()
