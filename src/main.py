from asyncio import run
from freelas.task.iter import iter

async def main():
    await iter()

run(main())