import logging
import numpy as np
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class BroadbandController(ModuleController):

    start_broadband_measurement = pyqtSignal()
    set_averages_failure = pyqtSignal()
    set_frequency_step_failure = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)
        

    @pyqtSlot(str, object)
    def process_signals(self, key: str, value: Measurement):
        if key == "measurement_data" and  self.module.model.current_broadband_measurement is not None:
            logger.debug("Received single measurement.")
            self.module.model.current_broadband_measurement.add_measurement(value)

        elif key == "failure_set_averages" and value == self.module.view._ui_form.averagesEdit.text():
            logger.debug("Received set averages failure.")
            self.set_averages_failure.emit()

        
    @pyqtSlot(str)
    def set_frequency(self, value):
        try:
            logger.debug("Setting frequency to: " + float(value))
            self.module.nqrduck_signal.emit("set_frequency", value)
        except ValueError:
            self.set_averages_failure.emit()
            self.set_frequency_step_failure.emit()

    @pyqtSlot(str)
    def set_averages(self, value):
        logger.debug("Setting averages to: " + value)
        self.module.nqrduck_signal.emit("set_averages", value)

    @pyqtSlot(str)
    def change_start_frequency(self, value):
        value = float(value)
        if value > self.module.model.MIN_FREQUENCY:
            self.module.model.start_frequency = value * 1e6
        else:
            self.module.model.start_frequency = self.module.model.MIN_FREQUENCY

    @pyqtSlot(str)
    def change_stop_frequency(self, value):
        value = float(value)
        if value < self.module.model.MAX_FREQUENCY:
            self.module._model.stop_frequency = value * 1e6
        else:
            self.module._model.stop_frequency = self.module.model.MAX_FREQUENCY

    @pyqtSlot(str)
    def change_frequency_step(self, value):
        try:
            logger.debug("Changing frequency step to: " + value)
            value = float(value) * 1e6
            if value > 0:
                self.module.model.frequency_step = value
        except  ValueError:
            logger.debug("Invalid frequency step value")


    @pyqtSlot()
    def start_broadband_measurement(self):
        logger.debug("Start measurement clicked")
        # Create a list of different frequency values that we need for our broadband measurement
        start_frequency = self.module.model.start_frequency
        stop_frequency = self.module.model.stop_frequency
        frequency_step = self.module.model.frequency_step

        frequency_list = np.arange(start_frequency, stop_frequency + frequency_step, frequency_step)
        logger.debug("Frequency list: " + str(frequency_list))

        # Create a new broadband measurement object
        self.module.model.current_broadband_measurement = self.module.model.BroadbandMeasurement(frequency_list, self.module.model.frequency_step)
        self.module.model.current_broadband_measurement.received_measurement.connect(self.module.view.on_broadband_measurement_added)
        self.module.model.current_broadband_measurement.received_measurement.connect(self.on_broadband_measurement_added)
        
        self.module.view.add_info_text("Starting broadband measurement.")
        # Start the first measurement
        self.module.view.add_info_text("Starting measurement at frequency: " + str(start_frequency))
        self.module.nqrduck_signal.emit("set_frequency", str(start_frequency))
        self.module.nqrduck_signal.emit("start_measurement", None)


    @pyqtSlot()
    def on_broadband_measurement_added(self):
        """This slot is called when a single measurement is added to the broadband measurement.
        It then checks if there are more frequencies to measure and if so, starts the next measurement.
        Furthermore it updates the plots.
        """
        logger.debug("Broadband measurement added.")
        # Check if there are more frequencies to measure
        if not self.module.model.current_broadband_measurement.is_complete():
            # Get the next frequency to measure
            next_frequency = self.module.model.current_broadband_measurement.get_next_measurement_frequency()
            logger.debug("Next frequency: " + str(next_frequency))
            # Start the next measurement
            self.module.view.add_info_text("Starting measurement at frequency: " + str(next_frequency))
            self.module.nqrduck_signal.emit("set_frequency", str(next_frequency))
            self.module.nqrduck_signal.emit("start_measurement", None)
        else:
            self.module.view.add_info_text("Broadband measurement finished.")