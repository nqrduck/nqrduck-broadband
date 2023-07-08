import logging
from PyQt5.QtCore import QMetaMethod, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)


class BroadbandView(ModuleView):

    start_measurement = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        self._connect_signals()
        

        self.init_plots()

    def _connect_signals(self) -> None:
        self._ui_form.start_frequencyField.editingFinished.connect(
            lambda: self.module._controller.change_start_frequency(
                self._ui_form.start_frequencyField.text()
            )
        )
        self._ui_form.stop_frequencyField.editingFinished.connect(
            lambda: self.module._controller.change_stop_frequency(
                self._ui_form.stop_frequencyField.text()
            )
        )

        self.module._model.start_frequency_changed.connect(self.on_start_frequency_change)
        self.module._model.stop_frequency_changed.connect(self.on_stop_frequency_change)
        
        self._ui_form.start_measurementButton.clicked.connect(lambda: self._start_measurement_clicked())
        self.start_measurement.connect(lambda: self.module._controller.start_measurement())

    def _start_measurement_clicked(self):
        # Create a QMessageBox object
        msg_box = QMessageBox()
        msg_box.setText("Start the measurement?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        # Set the default button to No
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Show the dialog and capture the user's choice
        choice = msg_box.exec_()
        
        # Process the user's choice
        if choice == QMessageBox.Yes:
            self.start_measurement.emit()
    
    def init_plots(self):
        # Initialization of broadband spectrum
        self._ui_form.broadbandPlot.canvas.ax.set_title("Broadband Spectrum")
        self._ui_form.broadbandPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.broadbandPlot.canvas.ax.set_xlabel("Frequency in MHz")
        self._ui_form.broadbandPlot.canvas.ax.set_ylabel("Amplitude a.u.")

        # Initialization of last measurement time domain
        self._ui_form.time_domainPlot.canvas.ax.set_title("Last Time Domain")
        self._ui_form.time_domainPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.time_domainPlot.canvas.ax.set_xlabel("time in us")
        self._ui_form.time_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")

        # Initialization of last measurement frequency domain
        self._ui_form.frequency_domainPlot.canvas.ax.set_title("Last Frequency Domain")
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlabel("time in us")
        self._ui_form.frequency_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")

    @pyqtSlot(float)
    def on_start_frequency_change(self, start_frequency):
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(left=start_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()

    @pyqtSlot(float)
    def on_stop_frequency_change(self, stop_frequency):
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(right=stop_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
