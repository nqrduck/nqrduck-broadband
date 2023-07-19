import logging
from collections import OrderedDict
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QObject
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class BroadbandModel(ModuleModel):
    MIN_FREQUENCY = 30.0
    MAX_FREQUENCY = 200.0
    DEFAULT_FREQUENCY_STEP = 0.1

    start_frequency_changed = pyqtSignal(float)
    stop_frequency_changed = pyqtSignal(float)

    def __init__(self, module) -> None:
        super().__init__(module)
        self.start_frequency = self.MIN_FREQUENCY
        self.stop_frequency = self.MAX_FREQUENCY
        self.DEFAULT_FREQUENCY_STEP = self.DEFAULT_FREQUENCY_STEP
        self.current_broadcast_measurement = None

    @property
    def start_frequency(self):
        return self._start_frequency

    @start_frequency.setter
    def start_frequency(self, value):
        self._start_frequency = value
        self.start_frequency_changed.emit(value)

    @property
    def stop_frequency(self):
        return self._stop_frequency

    @stop_frequency.setter
    def stop_frequency(self, value):
        self._stop_frequency = value
        self.stop_frequency_changed.emit(value)

    @property
    def frequency_step(self):
        return self._frequency_step
    
    @frequency_step.setter
    def frequency_step(self, value):
        self._frequency_step = value

    @property
    def current_broadcast_measurement(self):
        return self._current_broadcast_measurement
    
    @current_broadcast_measurement.setter
    def current_broadcast_measurement(self, value):
        self._current_broadcast_measurement = value

    class BroadbandMeasurement(QObject):
        """This class represents a single broadband measurement."""

        received_measurement = pyqtSignal()
        
        def __init__(self, frequencies) -> None:
            super().__init__()
            self._single_frequency_measurements = OrderedDict()
            for frequency in frequencies:
                self._single_frequency_measurements[frequency] = None

        def add_measurement(self, measurement):
            """This method adds a single measurement to the broadband measurement.
            
            Args:
                measurement (Measurement): The measurement object."""
            logger.debug("Adding measurement to broadband measurement at frequency: %s" % str(measurement.target_frequency))
            self._single_frequency_measurements[measurement.target_frequency] = measurement
            self.received_measurement.emit()
            QApplication.processEvents()

        def is_complete(self):
            """This method checks if all frequencies have been measured.
            
            Returns:
                bool: True if all frequencies have been measured, False otherwise."""
            for measurement in self._single_frequency_measurements.values():
                if measurement is None:
                    return False
            return True
        
        def get_next_measurement_frequency(self):
            """This method returns the next frequency that has to be measured.
            
            Returns:
                float: The next frequency that has to be measured."""
            for frequency, measurement in self._single_frequency_measurements.items():
                if measurement is None:
                    return frequency
                
        def get_last_completed_measurement(self):
            """ This method returns the last completed measurement.
            
            Returns:
                Measurement: The last completed measurement."""
            
            for frequency, measurement in self._single_frequency_measurements.items():
                if measurement is not None:
                    return measurement

        @property
        def single_frequency_measurements(self):
            """This property contains the dict of all frequencies that have to be measured."""
            return self._single_frequency_measurements
        
        @single_frequency_measurements.setter
        def single_frequency_measurements(self, value):
            self._single_frequency_measurements = value
