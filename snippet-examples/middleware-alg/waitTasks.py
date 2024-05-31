import asyncio

async def task1():
    await asyncio.sleep(2)
    return "Task 1 finished"

async def task2():
    await asyncio.sleep(3)
    return "Task 2 finished"

async def main():
    task1_coroutine = task1()
    task2_coroutine = task2()

    done, pending = await asyncio.wait([task1_coroutine, task2_coroutine], return_when=asyncio.FIRST_COMPLETED)

    # Get the result of the completed task
    result = done.pop().result()
    print(result)

    # Cancel the pending task
    for task in pending:
        task.cancel()

asyncio.run(main())
