from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    booking_base_url: str = "https://www.booking.com"
    headless: bool = True
    timeout: int = 30000
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    class Config:
        env_file = ".env"


settings = Settings()
