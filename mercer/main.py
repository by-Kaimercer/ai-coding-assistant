from client.llm_client import LLMClient
import asyncio

async def main():
    client = LLMClient()
    messages = [{"role": "user", "content": "What's up"}]
    
    # Corrected indentation below
    async for event in client.chat_completion(messages, False):
        # This code now correctly belongs to the loop
        print(event) 
    
    # It is good practice to close the client when done [5, 6]
    await client.close() 
    print("done")
    
asyncio.run(main())