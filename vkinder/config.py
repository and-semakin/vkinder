from pydantic import BaseSettings


class Config(BaseSettings):
    vk_user_tokens: str
    vk_group_token: str
    vk_group_id: int


config = Config()
