from threading import Thread
from datetime import datetime as dt
import time

import numpy as np

from lib import ClientFpsC
from lib import Logging
from lib import Resource


class MatrixThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.result = []

    def run(self):
        mm = MatrixMultiplicator(dimension=ClientFpsC.DIMENSION)
        mm.initialize_matrix()
        for thread_num in range(0, ClientFpsC.DIMENSION):
            t = Thread(
                target=mm.multiply_matrix,
                args=(int(thread_num), int(thread_num + 1)),
            )
            self.result.append(t)
            t.start()

        for thread_num in range(0, ClientFpsC.DIMENSION):
            self.result[thread_num].join()


class MatrixMultiplicator:
    """
    https://github.com/khalidgt95/Python-MultiThreading/blob/master/Matrix%20Multiplication.py
    """

    def __init__(self, dimension):
        self.dimension = dimension
        self.matrix_a = []
        self.matrix_b = []
        self.matrix_r = []

    def initialize_matrix(self):
        self.matrix_a = np.random.random((self.dimension, self.dimension))
        self.matrix_a *= 10
        self.matrix_a = self.matrix_a.astype(int)
        self.matrix_b = np.random.random((self.dimension, self.dimension))
        self.matrix_b *= 10
        self.matrix_b = self.matrix_b.astype(int)
        self.matrix_r = np.zeros((self.dimension, self.dimension)).astype(int)

    def multiply_matrix(self, start, end):
        for i in range(start, end):
            for j in range(self.dimension):
                for k in range(self.dimension):
                    self.matrix_r[i][j] += int(self.matrix_a[i][k] * self.matrix_b[k][j])


def calc_time(start):
    result = (dt.now() - start).total_seconds()
    return result


if __name__ == "__main__":
    res = Resource()
    log = Logging()
    counter = 0
    success = 0

    start = dt.now()
    for _ in range(1, ClientFpsC.MAX_TIME + 1):
        for _ in range(1, ClientFpsC.FPS + 1):
            counter += 1
            mt = MatrixThread()
            target_time = time.perf_counter() + 1 / ClientFpsC.FPS
            while time.perf_counter() < target_time:
                pass
            mt.start()
            res.get_usage()
            res.show_usage()
            log.info(
                state="SUCCESS",
                num=counter,
                message="Calculated",
                time=calc_time(start),
            )
            if calc_time(start) < 10:
                success += 1
    log.client_result(
        total_time=(dt.now() - start).total_seconds(),
        latency=(dt.now() - start).total_seconds() - ClientFpsC.MAX_TIME,
        success=success,
        total=(ClientFpsC.FPS * ClientFpsC.MAX_TIME),
    )
