import asyncio

async def coro1():
    await asyncio.sleep(1)
    print("Coroutine 1 completed")

async def coro2():
    await asyncio.sleep(2)
    print("Coroutine 2 completed")

async def main():
    # Wait for coro1 and coro2 to complete concurrently
    print("something before gather")
    await asyncio.gather(coro1(), coro2())
    print("something after gather")


# Run the main coroutine
asyncio.run(main())
