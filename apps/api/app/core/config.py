from functools import lru_cache
from pydantic import BaseSettings, Field, EmailStr


class Settings(BaseSettings):
  app_name: str = "Medical Consulting Platform"
  api_v1_prefix: str = "/"
  secret_key: str = Field(default="super-secret-key", env="SECRET_KEY")
  algorithm: str = "HS256"
  access_token_expire_minutes: int = 60 * 24
  database_url: str = Field(default="postgresql://postgres:postgres@db:5432/app", env="DATABASE_URL")
  mailhog_host: str = Field(default="mailhog", env="MAILHOG_HOST")
  mailhog_port: int = Field(default=1025, env="MAILHOG_PORT")
  s3_bucket: str = Field(default="local-bucket", env="S3_BUCKET")
  s3_region: str = Field(default="us-east-1", env="S3_REGION")
  s3_endpoint: str | None = Field(default=None, env="S3_ENDPOINT")
  frontend_base_url: str = Field(default="http://localhost:3000", env="FRONTEND_BASE_URL")
  default_admin_email: EmailStr = Field(default="admin@example.com", env="ADMIN_EMAIL")

  class Config:
    case_sensitive = True


@lru_cache
def get_settings() -> Settings:
  return Settings()
