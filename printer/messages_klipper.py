import service.comm as comm


class CommunicationMessages:
    def send(self, message):
        if message:
            comm.send(message)

    def connect(self, port, baud, node_name):
        return {
        }

    def get_filelist(self, node_name):
        return {
            'parameters': {
                'node_name': node_name
            },
            'event': "klipper.get_filelist"
        }

    def start_print(self, selected_path, node_name):
        return {
            'parameters': {
                'node_name': node_name,
                'path': selected_path
            },
            'event': "klipper.print_start"
        }

    def stop_print(self, node_name):
        return {
            'parameters': {
                'node_name': node_name,
            },
            'event': "klipper.print_stop"
        }

    def pause_print(self, node_name):
        return {
            'parameters': {
                'node_name': node_name,
            },
            'event': "klipper.print_pause"
        }

    def resume_print(self, node_name):
        return {
            'parameters': {
                'node_name': node_name,
            },
            'event': "klipper.print_resume"
        }
