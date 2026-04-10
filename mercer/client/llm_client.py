import asyncio
from typing import Any
from openai import AsyncOpenAI, RateLimitError, APIConnectionError

class LLMClient:
    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        # Define max retries here so it's easy to change later [2]
        self.max_retries = 3 

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key="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",
                base_url="https://openrouter.ai/api/v1",
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def chat_completion(self, messages: list[dict[str, Any]], stream: bool = True):
        # 1. Get the client and set up settings OUTSIDE the loop [4]
        client = self.get_client()
        kwargs = {
            "model": "qwen/qwen-2.5-coder-32b-instruct:free",
            "messages": messages,
            "stream": stream,
        }

        # 2. The Retry Loop: This is the "Engineering" fix [1, 2]
        for attempt in range(self.max_retries + 5):
            try:
                if stream:
                    # We use 'async for' because stream_response is a generator [6]
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    # Non-stream waits for the whole answer [7]
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                
                # If successful, exit the function entirely [5]
                return 

            except RateLimitError as e:
                # 3. Exponential Backoff: Wait 1s, then 2s, then 4s... [3]
                if attempt < self.max_retries:
                    wait_time = 20 
                    print(f"Rate limited. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    print("Max retries reached. Error:", e)
                    raise e
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

    async def _stream_response(self, client: AsyncOpenAI, kwargs: dict[str, Any]):
        # This will be filled in later in the tutorial to handle chunks [8]
        pass

    async def _non_stream_response(self, client: AsyncOpenAI, kwargs: dict[str, Any]):
        # This gets the full response at once [7, 9]
        response = await client.chat.completions.create(**kwargs)
        return response