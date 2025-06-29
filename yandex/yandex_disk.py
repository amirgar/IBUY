import yadisk
from dotenv import load_dotenv
import os
import asyncio


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
YANDEX_TOKEN = os.environ.get("YANDEX_TOKEN")


async def get_data(YANDEX_TOKEN):
    async with yadisk.AsyncClient(token=YANDEX_TOKEN) as client:
        async for dir in client.listdir("/IBUY"): 
            try:
                current_dir = f"/IBUY/{dir['name']}"
                async for photo in client.listdir(current_dir)  :
                    # print("\t", photo['name'])
                    await client.download(f"{current_dir}/{photo['name']}", f'products_photos/{dir["name"]}/{photo['name']}')
            except Exception as e: 
                # print(e) 
                pass


if __name__ == "__main__": 
    asyncio.run(get_data(YANDEX_TOKEN))
