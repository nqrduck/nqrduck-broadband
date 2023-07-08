from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel


class BroadbandModel(ModuleModel):
    start_frequency_changed = pyqtSignal(float)
    stop_frequency_changed = pyqtSignal(float)

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
