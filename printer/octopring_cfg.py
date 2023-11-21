from printer.messages_octoprint import CommunicationMessages


class Config:
    def __init__(self):
        pass

    def configure(self, printer):
        printer.popup.add_port('VIRTUAL')
        printer.popup.add_port('/dev/ttyUSB0')
        printer.popup.add_port('/dev/ttyUSB1')
        printer.popup.add_port('/dev/ttyACM0')
        printer.popup.communication = CommunicationMessages()
        printer.popup.filelist.communication = printer.popup.communication
