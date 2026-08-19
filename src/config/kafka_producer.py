import json

from aiokafka import AIOKafkaProducer

from src.config.config import settings


def serializer(message):
    return json.dumps(message).encode()


class KafkaProducer:
    def __init__(self):
        self.producer = None

    async def start_producer(self,):
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
                value_serializer=serializer,
                compression_type="gzip",
                enable_idempotence=True,
                acks='all',
            )
            await self.producer.start()

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic: str, payload: dict, key: str | None = None):
        await self.producer.send_and_wait(
            topic=topic,
            value=payload,
            key=key.encode() if key else None,
        )
