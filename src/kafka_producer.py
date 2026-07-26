import asyncio
import json
import random

from aiokafka import AIOKafkaProducer

from src.utils.config import settings


def serializer(message):
    return json.dumps(message).encode()


async def produce():
    producer = AIOKafkaProducer(
        bootstrap_servers=f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
        value_serializer=serializer,
        compression_type="gzip",
        enable_idempotence=True,
        acks='all',
    )

    await producer.start()

    try:
        while True:
            data = {
                "temp": random.randint(10, 20),
                "weather": random.choice(("rainy", "sunny"))

            }
            await producer.send(settings.KAFKA_TOPIC, data)
            await asyncio.sleep(random.randint(1, 5))
    finally:
        await producer.stop()


if __name__ == '__main__':
    asyncio.run(produce())