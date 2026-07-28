import os


class Settings:
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "asset-service")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str | None = os.getenv("JWT_ALGORITHM")

    VALID_ENVIRONMENTS = {"development", "staging", "production"}

    def validate(self):
        if not self.JWT_SECRET_KEY:
            raise RuntimeError("Missing required config: JWT_SECRET_KEY")

        if not self.JWT_ALGORITHM:
            raise RuntimeError("Missing required config: JWT_ALGORITHM")

        if self.ENVIRONMENT not in self.VALID_ENVIRONMENTS:
            raise RuntimeError(
                f"Invalid ENVIRONMENT value: {self.ENVIRONMENT}. "
                f"Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}"
            )


settings = Settings()
settings.validate()