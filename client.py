import time
from datetime import datetime as dt

import grpc
import file_pb2, file_pb2_grpc

from lib import Resource
from lib import Logging
from lib import MatrixGenerator
from lib import matrix_converter_bytes, matrix_converter_str
from lib import ClientFpsC, ClientDimensionC

import numpy as np


class ProcessingClient:
    def __init__(self, stub):
        self.res = Resource()
        self.log = Logging()
        self.stub = stub
        self.start = ""
        self.messages = []
        self.result = []
        self.success = 0
        self.counter = 0

    def calc_time(self):
        result = (dt.now() - self.start).total_seconds()
        return result

    def request_by_dimension(self):
        self.log.start(
            message="Start Request By Dimension Request",
            time=dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.start = dt.now()
        for d in ClientDimensionC.DIMENSIONS:
            mg = MatrixGenerator(dimension=d)
            mg.initialize_matrix()
            yield file_pb2.Request(
                dimension=mg.dimension,
                matrix_a=matrix_converter_bytes(mg.matrix_a),
                matrix_b=matrix_converter_bytes(mg.matrix_b),
            )

    def response_by_dimension(self):
        responses = self.stub.calculate(self.request_by_dimension())
        self.log.start(
            message="Start Response",
            time=dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        for r in responses:
            self.res.get_usage()
            self.res.show_usage()
            self.counter += 1
            self.log.info(
                state="SUCCESS",
                num=self.counter,
                message="Recieved",
                time=self.calc_time(),
            )
            self.success += 1
        self.log.client_result(
            total_time=(dt.now() - self.start).total_seconds(),
            latency=0,
            success=self.success,
            total=len(ClientDimensionC.DIMENSIONS),
        )
        # self.result = matrix_converter_str(r.matrix_r).reshape((r.dimension, r.dimension))

    def request_by_fps(self):
        self.log.start(
            message="Start Request By FPS Request",
            time=dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.start = dt.now()
        for _ in range(1, ClientFpsC.MAX_TIME + 1):
            for _ in range(1, ClientFpsC.FPS + 1):
                mg = MatrixGenerator(dimension=ClientFpsC.DIMENSION)
                mg.initialize_matrix()
                target_time = time.perf_counter() + 1 / ClientFpsC.FPS
                while time.perf_counter() < target_time:
                    pass
                yield file_pb2.Request(
                    dimension=mg.dimension,
                    matrix_a=matrix_converter_bytes(mg.matrix_a),
                    matrix_b=matrix_converter_bytes(mg.matrix_b),
                )

    def response_by_fps(self):
        responses = self.stub.calculate(self.request_by_fps())
        self.log.start(
            message="Start Response",
            time=dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        for r in responses:
            self.res.get_usage()
            self.res.show_usage()
            self.counter += 1
            if self.calc_time() < 10:
                self.log.info(
                    state="SUCCESS",
                    num=self.counter,
                    message="Recieved",
                    time=self.calc_time(),
                )
                self.success += 1
            else:
                self.log.info(
                    state="FAIL",
                    num=self.counter,
                    message="Not Recieved",
                    time=self.calc_time(),
                )
        self.log.client_result(
            total_time=(dt.now() - self.start).total_seconds(),
            latency=(dt.now() - self.start).total_seconds()
            - ClientFpsC.MAX_TIME,
            success=self.success,
            total=(ClientFpsC.FPS * ClientFpsC.MAX_TIME),
        )
        # self.result = matrix_converter_str(r.matrix_r).reshape((r.dimension, r.dimension))


def run():
    with grpc.insecure_channel("localhost:50052") as channel:
        stub = file_pb2_grpc.ProcessingServerStub(channel)
        client = ProcessingClient(stub)
        client.response_by_fps()


if __name__ == "__main__":
    run()
