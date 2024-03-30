import asyncio

class blah:
    def __init__(self) -> None:
        self._num = 0 
        self._tasks = set()

    async def wait_for_variable(self):
        print("waiting for variable")
        self._num += 1
        await asyncio.sleep(3)  # Simulate some asynchronous operation
        print(f"counter = {self._num}")
        return "Variable resolved"

    # TODO: Create a async function that runs infinitely, publishing to a sense_topic
        # will be cancelled only if a result returns from getting command
    async def task(self):
        while True:
            result = await self.wait_for_variable()
            if not result:
                # Add the current task back to the list of tasks
                print("result is None, adding it back to tasks")
                self.tasks.add(asyncio.create_task(self.task(self.tasks)))
                break
            print(result)
            await asyncio.sleep(1)  # Wait before checking again

async def main():
    neat = blah()
    neat._tasks.add(asyncio.create_task(neat.task()))
    #tasks.add(asyncio.create_task(task(tasks)))
    await asyncio.wait(neat._tasks, return_when=asyncio.FIRST_COMPLETED)
    await asyncio.gather(*neat._tasks)

asyncio.run(main())
