from PyQt5.QtCore import pyqtSignal, QObject
from core.module.module_model import ModuleModel


class Broadband(ModuleModel):
    start_frequency_changed = pyqtSignal(float)
    stop_frequency_changed = pyqtSignal(float)
    widget_changed = pyqtSignal(QObject)

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
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value
        self.widget_changed.emit(value)
