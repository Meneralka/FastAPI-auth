from pathlib import Path
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


class LoggerSettings(BaseSettings):
    file_format: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {function} - {message}"
    )
    cmd_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> -"
        " <level>{message}</level>"
    )
    rotation: str = "10 MB"
    retention: str = "10 days"
    compression: str = "zip"
    auth_logs: Path = BASE_DIR / "log_files" / "auth_logs"
    error_logs: Path = BASE_DIR / "log_files" / "error_logs"


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 10
    refresh_token_expire_days: int = 30


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"
    auth: str = "/auth"
    register_: str = "/register"


class RedisConfig(BaseModel):
    host: str = "redis"
    port: int = 6379
    db: int = 0
    decode_responses: bool = False


class Api(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 50
    pool_size: int = 10

    naming_convention: dict = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=r".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )

    run: RunConfig = RunConfig()
    api: Api = Api()
    redis: RedisConfig = RedisConfig()
    db: DatabaseConfig
    auth: AuthJWT = AuthJWT()
    logs: LoggerSettings = LoggerSettings()


settings = Settings()
