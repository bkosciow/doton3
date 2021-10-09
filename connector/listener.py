from .storage_pb2_grpc import *
from .storage_pb2 import *
import json
from threading import Thread


class Listener(Thread):
    def __init__(self, address):
        Thread.__init__(self)
        self.address = address
        self.channel = grpc.insecure_channel(address)
        self.stub = ProviderStub(self.channel)
        self.work = True
        self.widgets = {}
        self.connection_error = False

    def run(self):
        try:
            self._initialize_values()
            for response in self.stub.get_changes(EmptyRequest()):
                try:
                    response = json.loads(response.data)
                    key = list(response)[0]
                    self._dispatch_data(key, response[key])
                except ValueError as e:
                    response = None

                if not self.work:
                    break
        except grpc.RpcError as e:
            print("grpc crash")
            print(e)
            self.work = False
            self.connection_error = True

    def _initialize_values(self):
        for name in self.widgets:
            try:
                message = Request(key=name)
                response = self.stub.get_storage(message)
                response = json.loads(response.data)
                if response:
                    self._dispatch_data(name, response)
            except ValueError as e:
                print("Failed to load {} data." % (name))

    def stop(self):
        self.work = False

    def add_widget(self, name, widget):
        if name not in self.widgets:
            self.widgets[name] = []

        self.widgets[name].append(widget)

    def _dispatch_data(self, name, data):
        # print(name, "<>", data)
        if name in self.widgets:
            for widget in self.widgets[name]:
                widget.update_values(data, name)




