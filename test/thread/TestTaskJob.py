from xkits import TaskJob


def task(number: int):
    print(f"number: {number}")


if __name__ == "__main__":
    print((job := TaskJob.create_task(task, 1)).run())
    print(job.running_timer.created_time)
    print(job.running_timer.started_time)
    print(job.running_timer.stopped_time)
