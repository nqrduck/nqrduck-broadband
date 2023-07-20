import logging
import numpy as np
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
        
        def __init__(self, frequencies, frequency_step) -> None:
            super().__init__()
            self._single_frequency_measurements = OrderedDict()
            for frequency in frequencies:
                self._single_frequency_measurements[frequency] = None

            self.frequency_step = frequency_step

        def add_measurement(self, measurement):
            """This method adds a single measurement to the broadband measurement.
            
            Args:
                measurement (Measurement): The measurement object."""
            logger.debug("Adding measurement to broadband measurement at frequency: %s" % str(measurement.target_frequency))
            self._single_frequency_measurements[measurement.target_frequency] = measurement
            self.assemble_broadband_spectrum()
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
                
        def get_finished_percentage(self):
            """Get the percentage of measurements that have been finished.
            
            Returns:
                float: The percentage of measurements that have been finished."""
            
            finished_measurements = 0
            for measurement in self._single_frequency_measurements.values():
                if measurement is not None:
                    finished_measurements += 1
            return finished_measurements / len(self._single_frequency_measurements) * 100
        
        def assemble_broadband_spectrum(self):
            """This method assembles the broadband spectrum from the single frequency measurement data in frequency domain."""
            # First we get all of the single frequency measurements that have already been measured
            single_frequency_measurements = []
            for measurement in self._single_frequency_measurements.values():
                if measurement is not None:
                    single_frequency_measurements.append(measurement)

            logger.debug("Assembling broadband spectrum from %d single frequency measurements." % len(single_frequency_measurements))
            fdy_assembled = np.array([])
            fdx_assembled = np.array([])
            # We cut out step_size / 2 around 0 Hz of the spectrum and assemble the broadband spectrum
            for measurement in single_frequency_measurements:
                # This finds the center of the spectrum
                center = np.where(measurement.fdx == 0)[0][0]
                logger.debug("Center: %d" % center)
                # This finds the nearest index of the lower and upper frequency step
                logger.debug("Frequency step: %f" % self.frequency_step)
                logger.debug(measurement.fdx)
                idx_xf_lower = self.find_nearest(measurement.fdx, -self.frequency_step/2 * 1e-6) 
                idx_xf_upper = self.find_nearest(measurement.fdx, +self.frequency_step/2 * 1e-6)

                # This interpolates the y values of the lower and upper frequency step
                yf_interp_lower = np.interp(-self.frequency_step/2 * 1e-6, [measurement.fdx[idx_xf_lower], measurement.fdx[center]], 
                                        [measurement.fdy[idx_xf_lower][0], measurement.fdy[center][0]])
            
                yf_interp_upper = np.interp(+self.frequency_step/2 * 1e-6, [measurement.fdx[center], measurement.fdx[idx_xf_upper]], 
                                        [measurement.fdy[center][0], measurement.fdy[idx_xf_lower][0]]) 
                
                try:
                    fdy_assembled[-1] = (fdy_assembled[-1] + yf_interp_lower) / 2
                    fdy_assembled = np.append(fdy_assembled, measurement.fdy[center])
                    fdy_assembled = np.append(fdy_assembled, yf_interp_upper)
                    
                    fdx_assembled[-1] = -self.frequency_step/2 * 1e-6 + measurement.target_frequency * 1e-6
                    fdx_assembled = np.append(fdx_assembled, measurement.target_frequency * 1e-6)
                    fdx_assembled = np.append(fdx_assembled, +self.frequency_step/2 * 1e-6 + measurement.target_frequency * 1e-6)
                # On the first run we will get an Index Error
                except IndexError:
                    fdy_assembled = np.array([yf_interp_lower, measurement.fdy[center][0], yf_interp_upper])
                    first_time_values = np.array([-self.frequency_step/2*1e-6, measurement.fdx[center] , +self.frequency_step/2*1e-6]) + measurement.target_frequency*1e-6
                    fdx_assembled = first_time_values
            
            self.broadband_data_fdx = fdx_assembled.flatten()
            self.broadband_data_fdy = fdy_assembled.flatten()
                

        def find_nearest(self, array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx

        @property
        def single_frequency_measurements(self):
            """This property contains the dict of all frequencies that have to be measured."""
            return self._single_frequency_measurements
        
        @single_frequency_measurements.setter
        def single_frequency_measurements(self, value):
            self._single_frequency_measurements = value

        @property
        def broadband_data_fdx(self):
            """ This property contains the broadband data and is assembled by the differen single_frequency measurements in frequency domain."""
            return self._broadband_data_fdx

        @broadband_data_fdx.setter
        def broadband_data_fdx(self, value):
            self._broadband_data_fdx = value

        @property
        def broadband_data_fdy(self):
            """ This property contains the broadband data and is assembled by the differen single_frequency measurements in frequency domain."""
            return self._broadband_data_fdy
        
        @broadband_data_fdy.setter
        def broadband_data_fdy(self, value):
            self._broadband_data_fdy = value
