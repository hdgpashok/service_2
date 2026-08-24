import asyncio
import json

from aiokafka import AIOKafkaProducer

from src.config.config import settings


def serializer(message):
    return json.dumps(message).encode()


class KafkaProducer:
    def __init__(self):
        self.producer = None
        self._lock = asyncio.Lock()
        self.inflight = 0
        self._drained = asyncio.Event()
        self._drained.set()

    async def start_producer(self,):
        async with self._lock:
            if self.producer is not None:
                return

            self.producer = AIOKafkaProducer(
                bootstrap_servers=f'{settings.KAFKA_HOST}:{settings.KAFKA_PORT}',
                value_serializer=serializer,
                compression_type="gzip",
                enable_idempotence=True,
                acks='all',
            )
            await self.producer.start()

    async def stop_producer(self):
        async with self._lock:
            if self.producer is None:
                return

            producer = self.producer
            self.producer = None

            await self._drained.wait()
            await producer.stop()

    async def send(self, topic: str, payload: dict, key: str | None = None):
        if self.producer is None:
            raise RuntimeError(
                "KafkaProducer.send() called before start_producer() — "
                "producer is not initialized"
            )
        self.inflight += 1
        self._drained.clear()

        try:
            await self.producer.send_and_wait(
                topic=topic,
                value=payload,
                key=key.encode() if key else None,
            )
        finally:
            self.inflight -= 1
            if self.inflight == 0:
                self._drained.set()
