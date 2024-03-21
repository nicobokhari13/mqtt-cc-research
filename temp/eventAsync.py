import asyncio

async def waiter(event):
    print('waiting for it ...')
    await event.wait()
    print("after await")
    print('... got it!')

async def main():
    # Create an Event object.
    print("creating event")
    event = asyncio.Event()

    # Spawn a Task to wait until 'event' is set.
    waiter_task = asyncio.create_task(waiter(event))
    print("spawned waiter task")
    # Sleep for 1 second and set the event.
    print("waiting for a second")
    await asyncio.sleep(8)
    print("setting the event")
    event.set()
    print("waiting for the waiter task")
    # Wait until the waiter task is finished.
    await waiter_task
    print("finished waiter task")

asyncio.run(main())
