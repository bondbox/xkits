from time import sleep

from xarg import task_pool


def task(number: int):
    print(f"number: {number}")
    sleep(number % 3 + 1)


with task_pool(workers=4) as executor:
    for n in range(1, 10):
        executor.submit(task, n)
    print("tasks submitted")
    executor.barrier()
    print("task barrier")
    for n in range(1, 10):
        executor.submit(task, n)
    print("all tasks submitted")
    # executor.barrier()
    for jid, job in executor.items():
        if not job.stopped:
            print(f"job {jid} not stopped")
