import logging
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication

from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)


class BroadbandView(ModuleView):

    start_broadband_measurement = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        logger.debug("Facecolor %s" % str(self._ui_form.broadbandPlot.canvas.ax.get_facecolor()))

        self._connect_signals()
    
        self.init_plots()

    def _connect_signals(self) -> None:
        self._ui_form.start_frequencyField.editingFinished.connect(
            lambda: self.module.controller.change_start_frequency(
                self._ui_form.start_frequencyField.text()
            )
        )
        self._ui_form.stop_frequencyField.editingFinished.connect(
            lambda: self.module.controller.change_stop_frequency(
                self._ui_form.stop_frequencyField.text()
            )
        )

        self._ui_form.frequencystepEdit.editingFinished.connect(
            lambda: self.module.controller.change_frequency_step(
                self._ui_form.frequencystepEdit.text()
            )
        )

        self.module.model.start_frequency_changed.connect(self.on_start_frequency_change)
        self.module.model.stop_frequency_changed.connect(self.on_stop_frequency_change)
        
        self._ui_form.start_measurementButton.clicked.connect(self._start_measurement_clicked)
        self.start_broadband_measurement.connect(self.module._controller.start_broadband_measurement)

        self._ui_form.averagesEdit.editingFinished.connect(lambda: self.on_editing_finished(self._ui_form.averagesEdit.text()))

        self.module.controller.set_averages_failure.connect(self.on_set_averages_failure)
        self.module.controller.set_frequency_step_failure.connect(self.on_set_frequency_step_failure)

    def _start_measurement_clicked(self):
        # Create a QMessageBox object
        msg_box = QMessageBox()
        msg_box.setText("Start the measurement?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Set the default button to No
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Show the dialog and capture the user's choice
        choice = msg_box.exec()
        
        # Process the user's choice
        if choice == QMessageBox.StandardButton.Yes:
            self.start_broadband_measurement.emit()
    
    def init_plots(self):

        # Initialization of broadband spectrum
        self._ui_form.broadbandPlot.canvas.ax.set_title("Broadband Spectrum")
        self._ui_form.broadbandPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.broadbandPlot.canvas.ax.set_xlabel("Frequency in MHz")
        self._ui_form.broadbandPlot.canvas.ax.set_ylabel("Amplitude a.u.")
        self._ui_form.broadbandPlot.canvas.ax.grid()

        # Initialization of last measurement time domain
        self._ui_form.time_domainPlot.canvas.ax.set_title("Last Time Domain")
        self._ui_form.time_domainPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.time_domainPlot.canvas.ax.set_xlabel("time in us")
        self._ui_form.time_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")
        self._ui_form.time_domainPlot.canvas.ax.grid()

        # Initialization of last measurement frequency domain
        self._ui_form.frequency_domainPlot.canvas.ax.set_title("Last Frequency Domain")
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlim([0, 250])
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlabel("time in us")
        self._ui_form.frequency_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")
        self._ui_form.frequency_domainPlot.canvas.ax.grid()

    @pyqtSlot(float)
    def on_start_frequency_change(self, start_frequency):
        logger.debug("Adjusting view to new start frequency: " + str(start_frequency))
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(left=start_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
        self._ui_form.start_frequencyField.setText(str(start_frequency* 1e-6))

    @pyqtSlot(float)
    def on_stop_frequency_change(self, stop_frequency):
        logger.debug("Adjusting view to new stop frequency: " + str(stop_frequency))
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(right=stop_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
        self._ui_form.stop_frequencyField.setText(str(stop_frequency* 1e-6))

    @pyqtSlot()
    def on_editing_finished(self, value):
        logger.debug("Editing finished by.")
        self.sender().setStyleSheet("")
        if self.sender() == self._ui_form.averagesEdit:
            self.module.controller.set_averages(value)

    @pyqtSlot()
    def on_set_averages_failure(self):
        logger.debug("Set averages failure.")
        self._ui_form.averagesEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_set_frequency_step_failure(self):
        logger.debug("Set frequency step failure.")
        self._ui_form.frequencystepEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_broadband_measurement_added(self):
        # Get last measurement from the broadband measurement object that is not None
        logger.debug("Updating broadband plot.")
        measurement = self.module.model.current_broadcast_measurement.get_last_completed_measurement()

        td_plotter = self._ui_form.time_domainPlot.canvas.ax
        fd_plotter = self._ui_form.frequency_domainPlot.canvas.ax

        td_plotter.clear()
        fd_plotter.clear()

        td_plotter.plot(measurement.tdx, measurement.tdy)
        fd_plotter.plot(measurement.fdx, measurement.fdy)

        self._ui_form.time_domainPlot.canvas.draw()
        self._ui_form.frequency_domainPlot.canvas.draw()

        QApplication.processEvents()

