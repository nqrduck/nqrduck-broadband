"""This module contains the view of the broadband module."""
import logging
from datetime import datetime
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication, QLabel, QVBoxLayout
from nqrduck.assets.icons import Logos
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)


class BroadbandView(ModuleView):
    """View class for the Broadband module.
    
    Signals:
        start_broadband_measurement: Signal to start a broadband measurement.
    """
    start_broadband_measurement = pyqtSignal()

    def __init__(self, module):
        """Initializes the BroadbandView."""
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        logger.debug(
            f"Facecolor {str(self._ui_form.broadbandPlot.canvas.ax.get_facecolor())}"
        )

        self.connect_signals()

        # Add logos
        self._ui_form.start_measurementButton.setIcon(Logos.Play_16x16())
        self._ui_form.start_measurementButton.setIconSize(
            self._ui_form.start_measurementButton.size()
        )

        self._ui_form.exportButton.setIcon(Logos.Save16x16())
        self._ui_form.exportButton.setIconSize(self._ui_form.exportButton.size())

        self._ui_form.importButton.setIcon(Logos.Load16x16())
        self._ui_form.importButton.setIconSize(self._ui_form.importButton.size())

        self.init_plots()

        self._ui_form.scrollAreaWidgetContents.setLayout(QVBoxLayout())
        self._ui_form.scrollAreaWidgetContents.layout().setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

    def connect_signals(self) -> None:
        """Connect the signals of the view to the slots of the controller."""
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

        self.module.model.start_frequency_changed.connect(
            self.on_start_frequency_change
        )
        self.module.model.stop_frequency_changed.connect(self.on_stop_frequency_change)
        self.module.model.frequency_step_changed.connect(self.on_frequency_step_change)

        self._ui_form.start_measurementButton.clicked.connect(
            self.start_measurement_clicked
        )
        self.start_broadband_measurement.connect(
            self.module._controller.start_broadband_measurement
        )

        self._ui_form.averagesEdit.editingFinished.connect(
            lambda: self.on_editing_finished(self._ui_form.averagesEdit.text())
        )

        self.module.controller.set_averages_failure.connect(
            self.on_set_averages_failure
        )
        self.module.controller.set_frequency_step_failure.connect(
            self.on_set_frequency_step_failure
        )

        # LUT data
        self.module.model.LUT_changed.connect(self.on_LUT_changed)

        # On deleteLUTButton clicked
        self._ui_form.deleteLUTButton.clicked.connect(self.module.controller.delete_LUT)

        # Save and load buttons
        self._ui_form.exportButton.clicked.connect(self.on_save_button_clicked)
        self._ui_form.importButton.clicked.connect(self.on_load_button_clicked)

    @pyqtSlot()
    def start_measurement_clicked(self) -> None:
        """This method is called when the start measurement button is clicked.

        It shows a dialog asking the user if he really wants to start the measurement.
        If the user clicks yes the start_broadband_measurement signal is emitted.
        """
        # Create a QMessageBox object
        msg_box = QMessageBox(parent=self)
        msg_box.setText("Start the measurement?")
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        # Set the default button to No
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Show the dialog and capture the user's choice
        choice = msg_box.exec()

        # Process the user's choice
        if choice == QMessageBox.StandardButton.Yes:
            self.start_broadband_measurement.emit()

    @pyqtSlot()
    def on_save_button_clicked(self) -> None:
        """This method is called when the save button is clicked.

        It shows a file dialog to the user to select a file to save the measurement to.
        """
        logger.debug("Save button clicked.")
        file_manager = self.FileManager(
            self.module.model.FILE_EXTENSION, parent=self.widget
        )
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_measurement(file_name)

    @pyqtSlot()
    def on_load_button_clicked(self) -> None:
        """This method is called when the load button is clicked.

        It shows a file dialog to the user to select a file to load the measurement from.
        """
        logger.debug("Load button clicked.")
        file_manager = self.FileManager(
            self.module.model.FILE_EXTENSION, parent=self.widget
        )
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_measurement(file_name)

    def init_plots(self) -> None:
        """Initialize the plots."""
        # Initialization of broadband spectrum
        self._ui_form.broadbandPlot.canvas.ax.set_xlim([0, 250])
        self.set_broadband_labels()

        # Initialization of last measurement time domain
        self._ui_form.time_domainPlot.canvas.ax.set_xlim([0, 250])
        self.set_timedomain_labels()

        # Initialization of last measurement frequency domain
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlim([0, 250])
        self.set_frequencydomain_labels()

    def set_timedomain_labels(self) -> None:
        """Set the labels of the time domain plot."""
        self._ui_form.time_domainPlot.canvas.ax.set_title("Last Time Domain")
        self._ui_form.time_domainPlot.canvas.ax.set_xlabel("time in us")
        self._ui_form.time_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")
        self._ui_form.time_domainPlot.canvas.ax.grid()

    def set_frequencydomain_labels(self) -> None:
        """Set the labels of the frequency domain plot."""
        self._ui_form.frequency_domainPlot.canvas.ax.set_title("Last Frequency Domain")
        self._ui_form.frequency_domainPlot.canvas.ax.set_xlabel("Frequency in MHz")
        self._ui_form.frequency_domainPlot.canvas.ax.set_ylabel("Amplitude a.u.")
        self._ui_form.frequency_domainPlot.canvas.ax.grid()

    def set_broadband_labels(self) -> None:
        """Set the labels of the broadband plot."""
        self._ui_form.broadbandPlot.canvas.ax.set_title("Magnitude Plot")
        self._ui_form.broadbandPlot.canvas.ax.set_xlabel("Frequency in MHz")
        self._ui_form.broadbandPlot.canvas.ax.set_ylabel("Magnitude a.u.")
        self._ui_form.broadbandPlot.canvas.ax.grid()

    @pyqtSlot(float)
    def on_start_frequency_change(self, start_frequency: float) -> None:
        """This method is called when the start frequency is changed.

        It adjusts the view to the new start frequency.

        Args:
            start_frequency (float) : The new start frequency.
        """
        logger.debug(
            "Adjusting view to new start frequency: " + str(start_frequency * 1e-6)
        )
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(left=start_frequency * 1e-6)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
        self._ui_form.start_frequencyField.setText(str(start_frequency * 1e-6))

    @pyqtSlot(float)
    def on_stop_frequency_change(self, stop_frequency: float) -> None:
        """This method is called when the stop frequency is changed.

        It adjusts the view to the new stop frequency.

        Args:
            stop_frequency (float) : The new stop frequency.
        """
        logger.debug(
            "Adjusting view to new stop frequency: " + str(stop_frequency * 1e-6)
        )
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(right=stop_frequency * 1e-6)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
        self._ui_form.stop_frequencyField.setText(str(stop_frequency * 1e-6))

    @pyqtSlot(float)
    def on_frequency_step_change(self, frequency_step: float) -> None:
        """This method is called when the frequency step is changed.

        It adjusts the view to the new frequency step.

        Args:
            frequency_step (float) : The new frequency step.
        """
        logger.debug(
            "Adjusting view to new frequency step: " + str(frequency_step * 1e-6)
        )
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(right=frequency_step * 1e-6)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()
        # Fix float representation
        frequency_step = str(f"{frequency_step * 1e-6:.2f}")
        self._ui_form.frequencystepEdit.setText(frequency_step)

    @pyqtSlot()
    def on_editing_finished(self, value: str) -> None:
        """This method is called when the user finished editing a field.

        It sets the value of the field in the model.

        Args:
            value (str) : The value of the field.
        """
        logger.debug("Editing finished by.")
        self.sender().setStyleSheet("")
        if self.sender() == self._ui_form.averagesEdit:
            self.module.controller.set_averages(value)

    @pyqtSlot()
    def on_set_averages_failure(self) -> None:
        """This method is called when the averages could not be set.

        It sets the border of the averages field to red indicating that the entered value was not valid.
        """
        logger.debug("Set averages failure.")
        self._ui_form.averagesEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_set_frequency_step_failure(self) -> None:
        """This method is called when the frequency step could not be set.

        It sets the border of the frequency step field to red indicating that the entered value was not valid.
        """
        logger.debug("Set frequency step failure.")
        self._ui_form.frequencystepEdit.setStyleSheet("border: 1px solid red;")

    @pyqtSlot()
    def on_broadband_measurement_added(self) -> None:
        """This method is called when a new broadband measurement is added to the model.

        It updates the plots and the progress bar.
        """
        # Get last measurement from the broadband measurement object that is not None
        logger.debug("Updating broadband plot.")
        measurement = self.module.model.current_broadband_measurement.get_last_completed_measurement()

        td_plotter = self._ui_form.time_domainPlot.canvas.ax
        fd_plotter = self._ui_form.frequency_domainPlot.canvas.ax
        broadband_plotter = self._ui_form.broadbandPlot.canvas.ax

        td_plotter.clear()
        fd_plotter.clear()
        broadband_plotter.clear()

        td_plotter.plot(
            measurement.tdx,
            measurement.tdy.real,
            label="Real",
            linestyle="-",
            alpha=0.35,
            color="red",
        )
        td_plotter.plot(
            measurement.tdx,
            measurement.tdy.imag,
            label="Imaginary",
            linestyle="-",
            alpha=0.35,
            color="green",
        )
        td_plotter.plot(
            measurement.tdx, abs(measurement.tdy), label="Magnitude", color="blue"
        )
        td_plotter.legend()

        fd_plotter.plot(
            measurement.fdx * 1e-6,
            measurement.fdy.real,
            label="Real",
            linestyle="-",
            alpha=0.35,
            color="red",
        )
        fd_plotter.plot(
            measurement.fdx * 1e-6,
            measurement.fdy.imag,
            label="Imaginary",
            linestyle="-",
            alpha=0.35,
            color="green",
        )
        fd_plotter.plot(
            measurement.fdx * 1e-6,
            abs(measurement.fdy),
            label="Magnitude",
            color="blue",
        )
        fd_plotter.legend()

        # Plot real and imag part again here in time and frequency domain
        broadband_plotter.plot(
            self.module.model.current_broadband_measurement.broadband_data_fdx,
            self.module.model.current_broadband_measurement.broadband_data_fdy,
        )

        # Plot S11 values on the twin axis of the broadband plot
        frequencies = self.module.model.current_broadband_measurement.reflection.keys()
        frequencies = [frequency * 1e-6 for frequency in frequencies]

        reflection_values = (
            self.module.model.current_broadband_measurement.reflection.values()
        )
        if reflection_values:
            self._ui_form.broadbandPlot.canvas.S11ax = (
                self._ui_form.broadbandPlot.canvas.ax.twinx()
            )
            S11plotter = self._ui_form.broadbandPlot.canvas.S11ax
            S11plotter.clear()
            # Make second axis for S11 value
            self._ui_form.broadbandPlot.canvas.S11ax.set_ylabel("S11 in dB")
            self._ui_form.broadbandPlot.canvas.S11ax.set_ylim([-40, 0])
            S11plotter.plot(
                frequencies,
                reflection_values,
                color="red",
                marker="x",
                linestyle="None",
            )

        self.set_timedomain_labels()
        self.set_frequencydomain_labels()
        self.set_broadband_labels()

        self._ui_form.time_domainPlot.canvas.draw()
        self._ui_form.frequency_domainPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.draw()

        value = int(
            self.module.model.current_broadband_measurement.get_finished_percentage()
        )
        logger.debug("Updating progress bar to: " + str(value))
        self._ui_form.measurementProgress.setValue(value)
        self._ui_form.measurementProgress.update()

        QApplication.processEvents()

    @pyqtSlot()
    def on_LUT_changed(self) -> None:
        """This method is called when the LUT data is changed."""
        logger.debug("Updating LUT fields.")
        # If lut is not None disable the start- stop step frequency fields and update the LUT type label
        if self.module.model.LUT is not None:
            self._ui_form.start_frequencyField.setEnabled(False)
            self._ui_form.stop_frequencyField.setEnabled(False)
            self._ui_form.frequencystepEdit.setEnabled(False)
            self._ui_form.activeLUTLabel.setText(self.module.model.LUT.TYPE)
        else:
            self._ui_form.start_frequencyField.setEnabled(True)
            self._ui_form.stop_frequencyField.setEnabled(True)
            self._ui_form.frequencystepEdit.setEnabled(True)
            self._ui_form.activeLUTLabel.setText("None")

    def add_info_text(self, text: str) -> None:
        """Add a text to the info box with a timestamp.

        Args:
            text (str): The text to add to the info box.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"[{timestamp}] {text}"
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 25px;")
        self._ui_form.scrollAreaWidgetContents.layout().addWidget(text_label)
