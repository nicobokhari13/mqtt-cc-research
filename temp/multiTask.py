import asyncio

class blah:
    def __init__(self) -> None:
        self._num = 0
        self._tasks = set()
        self._answer = None

    async def wait_for_variable(self):
        print("waiting for variable")
        #self._num += 1
        await asyncio.sleep(3)  # Simulate some asynchronous operation
        #print(f"counter = {self._num}")
        return "Variable resolved"

        # will be cancelled only if a result returns from getting command
    async def task(self, delay):
        while True:
            result = await self.wait_for_variable()
            print("waiting for delay:", delay)
            if not result:
                # Add the current task back to the list of tasks
                print("result is None, adding it back to tasks")
                self.tasks.add(asyncio.create_task(self.task(self.tasks)))
                break
            print(result)
            await asyncio.sleep(delay)  # Wait before checking again
            self._answer.set_result(42)

    async def blah(self):
        command = await self._answer
        return command

async def main():
    neat = blah()
    delays = [2,4,8]
    neat._answer = asyncio.get_event_loop().create_future()
    routines = [neat.task(time) for time in delays]
    for item in routines:
        neat._tasks.add(asyncio.create_task(item))
    # neat._tasks.add(asyncio.create_task(item) for item in routines)
    waiting_for_cmd = asyncio.ensure_future(neat.blah())
    neat._tasks.add(waiting_for_cmd)
    #tasks.add(asyncio.create_task(task(tasks)))
    done, pending = await asyncio.wait(neat._tasks, return_when=asyncio.FIRST_COMPLETED)
    #await asyncio.gather(*neat._tasks)
    if waiting_for_cmd in done:
        result = waiting_for_cmd.result()
        print(f"result from waiting cmd = {result}")
    else:
        print("done routine is not waiting for command")
asyncio.run(main())
