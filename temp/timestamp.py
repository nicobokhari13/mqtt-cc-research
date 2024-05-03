import asyncio

async def function_at_time(time_stamp):
    await asyncio.sleep(time_stamp / 1000)  # Convert milliseconds to seconds
    print(f"Executing function at {time_stamp} milliseconds")

async def execute_at_time_stamps(time_stamps):
    tasks = []
    for time_stamp in time_stamps:
        task = asyncio.create_task(function_at_time(time_stamp))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def main():
    time_stamps = [100, 131031, 772625, 886864, 687694]  # Example list of time stamps in milliseconds
    time_stamps.sort()
    await execute_at_time_stamps(time_stamps)

asyncio.run(main())
