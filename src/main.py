import uvicorn
import asyncio


async def main() -> None:
    uvicorn.run('application:get_app', host='0.0.0.0', port=8080, reload=True, factory=True)

if __name__ == '__main__':
    asyncio.run(main())