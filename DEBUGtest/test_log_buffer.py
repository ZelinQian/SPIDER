import spider
from spider.interface.BaseBenchmark import DummyBenchmark
from spider.planner_zoo import *
from spider.data.DataBuffer import LogBuffer
from spider.data.decorators import logbuffer_plan


def test1():
    # 用log_buffer.apply_to(planner)启用
    benchmark = DummyBenchmark({
        "snapshot": False
    })

    planner = LatticePlanner({
        "steps": 20,
        "dt": 0.2,
        "print_info": False
    })

    log_buffer = LogBuffer(
        file_prefix='log',
        autosave_max_intervals=50,
        file_format=spider.DATASET_FORMAT_JSON
        # file_format=spider.DATASET_FORMAT_RAW
    )

    log_buffer.apply_to(planner)

    for episode in range(3):
        benchmark.test(planner)

    log_buffer.release()


def test2():
    """
    用logbuffer_plan装饰器启用
    """
    class ClosedLoopPlanner(LatticePlanner):
        @logbuffer_plan
        def plan(self, *args, **kwargs):
            return super(ClosedLoopPlanner, self).plan(*args, **kwargs)

    benchmark = DummyBenchmark({
        "snapshot": False
    })

    planner = ClosedLoopPlanner({
        "steps": 20,
        "dt": 0.2,
        "print_info": False
    })

    log_buffer = LogBuffer(
        file_prefix='log',
        autosave_max_intervals=50,
        file_format=spider.DATASET_FORMAT_JSON
    )

    planner.set_log_buffer(log_buffer)

    for episode in range(3):
        benchmark.test(planner)

    log_buffer.release()


if __name__ == '__main__':
    test1()
