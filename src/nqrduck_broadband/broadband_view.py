import logging
from PyQt5.QtWidgets import QWidget
from nqrduck.module.module_view import ModuleView
from .broadband_widget import Ui_Form

logger = logging.getLogger(__name__)


class BroadbandView(ModuleView):
    def __init__(self, _model, controller):
        super().__init__(_model, controller)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(widget)
        self._model.widget = widget

        self._ui_form.start_frequencyField.editingFinished.connect(
            lambda: self._controller.change_start_frequency(
                self._ui_form.start_frequencyField.text()
            )
        )
        self._ui_form.stop_frequencyField.editingFinished.connect(
            lambda: self._controller.change_stop_frequency(
                self._ui_form.stop_frequencyField.text()
            )
        )

        self._model.start_frequency_changed.connect(self.on_start_frequency_change)
        self._model.stop_frequency_changed.connect(self.on_stop_frequency_change)

        self.init_plots()

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

    def on_start_frequency_change(self, start_frequency):
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(left=start_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()

    def on_stop_frequency_change(self, stop_frequency):
        self._ui_form.broadbandPlot.canvas.ax.set_xlim(right=stop_frequency)
        self._ui_form.broadbandPlot.canvas.draw()
        self._ui_form.broadbandPlot.canvas.flush_events()