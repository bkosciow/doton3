from printer.messages_klipper import CommunicationMessages


class Config:
    def __init__(self):
        pass

    def configure(self, printer):
        printer.popup.communication = CommunicationMessages()
        printer.popup.filelist.communication = printer.popup.communication
