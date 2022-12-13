from threading import Thread
from datetime import datetime as dt
from concurrent import futures

import grpc
import file_pb2
import file_pb2_grpc

from lib import Resource
from lib import Logging
from lib import MatrixMultiplicator
from lib import matrix_converter_bytes, matrix_converter_str


class ProcessingServer(file_pb2_grpc.ProcessingServerServicer):
    def __init__(self):
        self.res = Resource()
        self.log = Logging()
        self.result = []

    def calculate(self, request_iterator, context):
        for request in request_iterator:
            self.log.start(
                message=f"Matrix Demension : {request.dimension}",
                time=dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            mm = MatrixMultiplicator(
                dimension=request.dimension,
                matrix_a=matrix_converter_str(request.matrix_a),
                matrix_b=matrix_converter_str(request.matrix_b),
            )
            for thread_num in range(0, request.dimension):
                t = Thread(
                    target=mm.multiply_matrix,
                    args=(int(thread_num), int(thread_num + 1)),
                )
                self.result.append(t)
                t.start()
                print(f"[START THREADING]\t{dt.now()}")

            for thread_num in range(0, request.dimension):
                print(f"[END THREADING]\t{dt.now()}")
                self.result[thread_num].join()
            yield file_pb2.Response(
                dimension=mm.dimension,
                matrix_r=matrix_converter_bytes(mm.matrix_r),
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_pb2_grpc.add_ProcessingServerServicer_to_server(ProcessingServer(), server)
    try:
        print("Start Server. Listening on port 50052")
        server.add_insecure_port("[::]:50052")
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Stop Server")
        server.stop(0)


if __name__ == "__main__":
    serve()
