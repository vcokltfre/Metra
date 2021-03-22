from asyncpg import create_pool
from os import getenv
from json import dumps

from loguru import logger


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        self.guilds = {}

    async def setup(self):
        logger.info("Setting up database...")
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )
        logger.info("Database setup complete.")

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def create_event(self, type: str, data: dict, channel: int = None, category: int = None, user: int = None):
        data = dumps(data)

        await self.execute(
            "INSERT INTO Events (event_type, event_data, channel, category, user) VALUES ($1, $2, $3, $4, $5);",
            type, data, channel, category, user,
        )
