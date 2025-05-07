import asyncio
import json
from typing import Dict, List, AsyncGenerator
from fastapi import Request

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, List[asyncio.Queue]] = {}

    def _get_or_create_queues(self, project_token: str) -> List[asyncio.Queue]:
        if project_token not in self.connections:
            self.connections[project_token] = []
        return self.connections[project_token]

    async def push(self, project_token: str, log_data: dict):
        queues = self._get_or_create_queues(project_token)
        data_str = json.dumps(log_data, default=str)
        for queue in queues:
            await queue.put(data_str)

    async def listen(self, project_token: str, request: Request) -> AsyncGenerator[str, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self._get_or_create_queues(project_token).append(queue)

        try:
            while True:
                if await request.is_disconnected():
                    break

                data = await queue.get()
                yield f"data: {data}\n\n"
        finally:
            self.connections[project_token].remove(queue)

sse_manager = SSEManager()
