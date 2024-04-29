"""This module contains the BroadbandController class."""

import logging
import numpy as np
import json
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
from nqrduck_spectrometer.measurement import Measurement
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)


class BroadbandController(ModuleController):
    """Controller class for the Broadband module.

    Signals:
        start_broadband_measurement: Signal to start a broadband measurement.
        set_averages_failure: Signal that the set averages command failed.
        set_frequency_step_failure: Signal that the set frequency step command failed.
    """

    start_broadband_measurement = pyqtSignal()
    set_averages_failure = pyqtSignal()
    set_frequency_step_failure = pyqtSignal()

    def __init__(self, module):
        """Initializes the BroadbandController."""
        super().__init__(module)

    @pyqtSlot(str, object)
    def process_signals(self, key: str, value: object) -> None:
        """Process incoming signal from the nqrduck module.

        Args:
            key (str): Name of the signal.
            value (object): Value of the signal.
        """
        logger.debug(self.module.model.waiting_for_tune_and_match)

        if (
            key == "measurement_data"
            and self.module.model.current_broadband_measurement is not None
        ):
            logger.debug("Received single measurement.")
            self.module.model.current_broadband_measurement.add_measurement(value)

        elif (
            key == "failure_set_averages"
            and value == self.module.view._ui_form.averagesEdit.text()
        ):
            logger.debug("Received set averages failure.")
            self.set_averages_failure.emit()
        # receive LUT data
        elif key == "LUT_finished":
            self.received_LUT(value)

        elif (
            key == "confirm_tune_and_match"
            and self.module.model.waiting_for_tune_and_match
        ):
            logger.debug("Confirmed tune and match.")
            reflection = value
            logger.debug("Reflection: " + str(reflection))
            if reflection is not None:
                self.module.model.current_broadband_measurement.add_tune_and_match(
                    reflection
                )
            self.module.nqrduck_signal.emit("start_measurement", None)
            QApplication.processEvents()
            self.module.model.waiting_for_tune_and_match = False

    def received_LUT(self, LUT: Measurement) -> None:
        """This slot is called when the LUT data is received from the nqrduck module.

        Args:
            LUT (Measurement): LUT data.
        """
        logger.debug("Received LUT data.")
        self.module.model.LUT = LUT
        self.change_start_frequency(self.module.model.LUT.start_frequency)
        self.change_stop_frequency(self.module.model.LUT.stop_frequency)
        self.change_frequency_step(self.module.model.LUT.frequency_step)

    @pyqtSlot(str)
    def set_frequency(self, value: str) -> None:
        """Emits the set frequency signal to the nqrduck module.

        Args:
            value (str): Frequency in MHz.
        """
        try:
            logger.debug("Setting frequency to: " + float(value))
            self.module.nqrduck_signal.emit("set_frequency", value)
        except ValueError:
            self.set_averages_failure.emit()
            self.set_frequency_step_failure.emit()

    @pyqtSlot(str)
    def set_averages(self, value: str) -> None:
        """Emits the set averages signal to the nqrduck module.

        Args:
            value (str): Number of averages.
        """
        logger.debug("Setting averages to: " + value)
        self.module.nqrduck_signal.emit("set_averages", value)

    @pyqtSlot(str)
    def change_start_frequency(self, value: str) -> None:
        """Changes the start frequency of the measurement."""
        value = float(value)
        if value > self.module.model.MIN_FREQUENCY:
            self.module.model.start_frequency = value * 1e6
        else:
            self.module.model.start_frequency = self.module.model.MIN_FREQUENCY

    @pyqtSlot(str)
    def change_stop_frequency(self, value: str) -> None:
        """Changes the stop frequency of the measurement."""
        value = float(value)
        if value < self.module.model.MAX_FREQUENCY:
            self.module._model.stop_frequency = value * 1e6
        else:
            self.module._model.stop_frequency = self.module.model.MAX_FREQUENCY

    @pyqtSlot(str)
    def change_frequency_step(self, value: str) -> None:
        """Changes the frequency step of the measurement."""
        try:
            value = float(value) * 1e6
            if value > 0:
                self.module.model.frequency_step = value
        except ValueError:
            logger.debug("Invalid frequency step value")

    @pyqtSlot()
    def start_broadband_measurement(self) -> None:
        """Starts a broadband measurement."""
        logger.debug("Start measurement clicked")
        # Create a list of different frequency values that we need for our broadband measurement
        start_frequency = self.module.model.start_frequency
        stop_frequency = self.module.model.stop_frequency
        frequency_step = self.module.model.frequency_step

        frequency_list = np.arange(
            start_frequency, stop_frequency + frequency_step, frequency_step
        )
        logger.debug("Frequency list: " + str(frequency_list))

        # Create a new broadband measurement object
        self.module.model.current_broadband_measurement = (
            self.module.model.BroadbandMeasurement(
                frequency_list, self.module.model.frequency_step
            )
        )
        self.module.model.current_broadband_measurement.received_measurement.connect(
            self.module.view.on_broadband_measurement_added
        )
        self.module.model.current_broadband_measurement.received_measurement.connect(
            self.on_broadband_measurement_added
        )

        self.module.view.add_info_text("Starting broadband measurement.")
        # Start the first measurement
        QTimer.singleShot(500, lambda: self.start_single_measurement(start_frequency))
        QApplication.processEvents()

    @pyqtSlot()
    def on_broadband_measurement_added(self) -> None:
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
            QTimer.singleShot(
                500, lambda: self.start_single_measurement(next_frequency)
            )
            QApplication.processEvents()
        else:
            self.module.view.add_info_text("Broadband measurement finished.")

    @pyqtSlot()
    def delete_LUT(self) -> None:
        """This slot is called when the LUT is deleted."""
        self.module.model.LUT = None

    def start_single_measurement(self, frequency: float) -> None:
        """Starts a single measurement.

        Args:
            frequency (float): Frequency in MHz.
        """
        logger.debug("Starting single measurement.")
        self.module.view.add_info_text(
            "Starting measurement at frequency: " + str(frequency)
        )
        # First set the frequency of the spectrometer
        self.module.nqrduck_signal.emit("set_frequency", str(frequency))
        QApplication.processEvents()
        # If there is a LUT available, send the tune and match values as signal
        if self.module.model.LUT is not None:
            self.module.model.waiting_for_tune_and_match = True
            # We need the entry number of the LUT for the current frequency

            self.module.nqrduck_signal.emit("set_tune_and_match", frequency * 1e-6)
            QApplication.processEvents()
        else:
            self.module.nqrduck_signal.emit("start_measurement", None)
            self.module.model.waiting_for_tune_and_match = False
            QApplication.processEvents()

    def save_measurement(self, file_name: str) -> None:
        """Saves the current broadband measurement to a file.

        Args:
            file_name (str): Name of the file.
        """
        logger.debug("Saving measurement to file: " + file_name)
        self.module.view.add_info_text("Saving measurement to file: " + file_name)
        QApplication.processEvents()

        with open(file_name, "w") as f:
            json.dump(self.module.model.current_broadband_measurement.to_json(), f)

    def load_measurement(self, file_name: str) -> None:
        """Loads a broadband measurement from a file.

        Args:
            file_name (str): Name of the file.
        """
        logger.debug("Loading measurement from file: " + file_name)

        with open(file_name) as f:
            measurement = json.load(f)
            self.module.model.current_broadband_measurement = (
                self.module.model.BroadbandMeasurement.from_json(measurement)
            )
            self.module.view.add_info_text("Measurement loaded.")
            self.module.view.on_broadband_measurement_added()
            QApplication.processEvents()
