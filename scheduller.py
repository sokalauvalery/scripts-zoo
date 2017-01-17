from subprocess import Popen
from time import time
import asyncio
from asyncio import Queue
from concurrent.futures import ThreadPoolExecutor
import os


class State:
    running = 'Running'
    stopped = 'Stopped'
    pending = 'Pending'


class Task:
    taskid = 0

    def __init__(self, cmd, interval, timeout):
        Task.taskid += 1
        self.tid = Task.taskid
        self.cmd = cmd
        self.interval = interval
        self.timeout = timeout
        self.start_time = None
        self.finish_time = None
        self.state = State.stopped
        self.close = False
        self.id = cmd

    def delete(self):
        self.close = True

    @asyncio.coroutine
    def run(self):
        self.state = State.running
        print('Task {c} is running'.format(c=self.cmd) )
        proc = Popen(self.cmd, shell=True)
        self.start_time = time()
        status = None
        while True:
            status = proc.poll()
            if status is not None:
                break
                print('SUCCESS')
            if time() - self.start_time >= self.timeout:
                print('TIMEOUT EXCEEDED')
                break
                # print('FAIL')
                # break
            yield from asyncio.sleep(1)
        self.state = State.stopped
        self.finish_time = time()
        return status

    def __str__(self):
        return '{c} - {s}'.format(c=self.cmd, s=self.state)


class ConfigTask(Task):
    def __init__(self, task_str):
        self.task_str = task_str
        cmd, interval, timeout = self.parse(task_str)
        super().__init__(cmd, int(interval), int(timeout))

    def parse(self, task_str):
        return task_str.split("||")


class Scheduler:
    def __init__(self, config=None):
        self.task_map = {}
        self.tasks = Queue()
        self.workers = [self.worker(i) for i in range(3)]
        self.config_reader = self.config_reader()
        self.io_pool_exc = ThreadPoolExecutor()
        self.config = config

    def new(self, task):
        self.task_map[task.id] = task
        self.tasks.put_nowait(task)

    def delete(self, task):
        delete_task = self.task_map[task.id]
        delete_task.detete()
        del self.task_map[task.id]

    @asyncio.coroutine
    def config_update_watch(self):
        modified_at = os.path.getmtime(self.config)
        while True:
            if os.path.getmtime(self.config) == modified_at:
                yield from asyncio.sleep(1)
            return

    @asyncio.coroutine
    def config_reader(self):
        while True:
            if self.config and os.path.exists(self.config):
                config_tasks = []
                with open(self.config, 'r') as f:
                    file = yield from loop.run_in_executor(self.io_pool_exc, f.read)
                    for line in file.rstrip().split('\n'):
                        if not line == '':
                            config_tasks.append(ConfigTask(line))
                for task in self.task_map:
                    if task not in [t.id for t in config_tasks]:
                        self.task_map[task].delete()
                for task in config_tasks:
                    if task.id not in self.task_map:
                        self.new(task)
            yield from self.config_update_watch()

    @asyncio.coroutine
    def worker(self, id):
        while True:
            if not self.tasks.empty():
                task = self.tasks.get_nowait()
                if task.state == State.stopped:
                    if not task.finish_time or time() - task.finish_time > task.interval:
                        yield from task.run()
                if not task.close:
                    yield from self.tasks.put(task)
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def run_task(self, task):
        while True:
            print(task)
            if task.state == State.stopped:
                if not task.finish_time or time() - task.finish_time > task.interval:
                   #yield from self.workers.append(task.run())
                    yield from task.run()
        yield from asyncio.sleep(1)

    @asyncio.coroutine
    def run(self):
        while True:
            if not self.tasks.empty():
                task = self.tasks.get_nowait()
                print(task)
                if task.state == State.stopped:
                    if not task.finish_time or time() - task.finish_time > task.interval:
                       #yield from self.workers.append(task.run())
                        yield from task.run()
                yield from self.tasks.put(task)
        yield from asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    sched = Scheduler('/Users/sokalauvalery/shed_conf.txt')
    asyncio.ensure_future(sched.config_reader)
    loop.run_until_complete(asyncio.wait(sched.workers))
    loop.run_forever()
