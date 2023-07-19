import logging
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class BroadbandController(ModuleController):
    MIN_FREQUENCY = 30.0
    MAX_FREQUENCY = 200.0

    start_measurement = pyqtSignal()

    set_averages_failure = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)
        

    @pyqtSlot(str, object)
    def process_signals(self, key: str, value: Measurement):
        if key == "measurement_data":
            logger.debug("Received single measurement.")
            self.module.model.single_measurement = value

        elif key == "failure_set_averages" and value == self.module.view._ui_form.averagesEdit.text():
            logger.debug("Received set averages failure.")
            self.set_averages_failure.emit()
        
    @pyqtSlot(str)
    def set_frequency(self, value):
        logger.debug("Setting frequency to: " + value)
        self.module.nqrduck_signal.emit("set_frequency", value)

    @pyqtSlot(str)
    def set_averages(self, value):
        logger.debug("Setting averages to: " + value)
        self.module.nqrduck_signal.emit("set_averages", value)

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