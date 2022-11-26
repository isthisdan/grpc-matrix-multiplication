import os
import psutil

import numpy as np


class MatrixGenerator:
    """
    https://github.com/khalidgt95/Python-MultiThreading/blob/master/Matrix%20Multiplication.py
    """

    def __init__(self, dimension):
        self.dimension = dimension
        self.matrix_a = []
        self.matrix_b = []

    def initialize_matrix(self):
        self.matrix_a = np.random.random((self.dimension, self.dimension))
        self.matrix_a *= 10
        self.matrix_a = self.matrix_a.astype(int)
        self.matrix_b = np.random.random((self.dimension, self.dimension))
        self.matrix_b *= 10
        self.matrix_b = self.matrix_b.astype(int)


class MatrixMultiplicator:
    """
    https://github.com/khalidgt95/Python-MultiThreading/blob/master/Matrix%20Multiplication.py
    """

    def __init__(self, dimension, matrix_a, matrix_b):
        self.dimension = dimension
        self.matrix_a = matrix_a.reshape((self.dimension, self.dimension))
        self.matrix_b = matrix_b.reshape((self.dimension, self.dimension))
        self.matrix_r = np.zeros((self.dimension, self.dimension)).astype(int)

    def multiply_matrix(self, start, end):
        for i in range(start, end):
            for j in range(self.dimension):
                for k in range(self.dimension):
                    self.matrix_r[i][j] += int(
                        self.matrix_a[i][k] * self.matrix_b[k][j]
                    )


def matrix_converter_bytes(matrix):
    return matrix.tobytes()


def matrix_converter_str(matrix):
    matrix = np.frombuffer(matrix, dtype="int64")
    return matrix


class Resource:
    def __init__(self):
        self.pid = os.getpid()
        self.py = psutil.Process(self.pid)
        self.cpu_usage = ""
        self.memory_usage = ""

    def get_usage(self):
        self.cpu_usage = self.py.cpu_percent()
        self.memory_usage = self.py.memory_percent()

    def show_usage(self):
        print(
            f"[RESULT]\t PID: {self.pid}\t cpu usage: {self.cpu_usage}%\t memory usage : {self.memory_usage:.3f}%"
        )


class Logging:
    def start(self, message, time):
        print(f"[START]\t {message}\t {time}")

    def info(self, state, num, message, time):
        print(f"[{state}]\t Matrix #{num}\t {message}\t {time:.3f}")

    def end(self, message, time):
        print(f"[END]\t {message}\t {time}")

    def client_result(self, total_time, latency, success, total):
        reception_rate = (success / total) * 100
        print(
            f"[RESULT]\t Total Time: {total_time:.3f}s\t Latency: {latency:.3f}s\t Reception Rate: {reception_rate:.2f}%({success}/{total})"
        )


class ClientDimensionC:
    # DIMENSION =< 511(Approximately 4MB)
    # DIMENSION = 511 (1m 3s)
    DIMENSIONS = [10, 100, 200, 300, 400, 500]


class ClientFpsC:
    # DIMENSION < 40
    DIMENSION = 45
    MAX_TIME = 10
    FPS = 60
