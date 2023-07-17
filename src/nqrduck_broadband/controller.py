import logging
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class BroadbandController(ModuleController):
    MIN_FREQUENCY = 30.0
    MAX_FREQUENCY = 200.0

    start_measurement = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)

    @pyqtSlot(str)
    def change_start_frequency(self, value):
        value = float(value)
        if value > self.MIN_FREQUENCY:
            self.module._model.start_frequency = value
        else:
            self.module._model.start_frequency = self.MIN_FREQUENCY

    @pyqtSlot(str)
    def change_stop_frequency(self, value):
        value = float(value)
        if value < self.MAX_FREQUENCY:
            self.module._model.stop_frequency = value
        else:
            self.module._model.stop_frequency = self.MAX_FREQUENCY

    @pyqtSlot()
    def start_measurement(self):
        logger.debug("Start measurement clicked")
        self.module.nqrduck_signal.emit("start_measurement", None)