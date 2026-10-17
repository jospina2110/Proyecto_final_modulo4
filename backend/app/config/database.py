import asyncio
import logging

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import settings
from app.models import Appointment, Doctor, Patient

logger = logging.getLogger(__name__)

CONNECTION_ATTEMPTS = 10
RETRY_DELAY_SECONDS = 3


async def init_database() -> AsyncIOMotorClient:
    client = AsyncIOMotorClient(settings.mongo_uri, serverSelectionTimeoutMS=2000)
    for attempt in range(1, CONNECTION_ATTEMPTS + 1):
        try:
            await client.admin.command("ping")
            break
        except Exception as error:
            logger.warning("MongoDB no disponible (%s/%s): %s", attempt, CONNECTION_ATTEMPTS, error)
            if attempt == CONNECTION_ATTEMPTS:
                raise
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    await init_beanie(
        database=client[settings.mongo_db],
        document_models=[Patient, Doctor, Appointment],
    )
    return client
