from nqrduck.module.module_controller import ModuleController


class BroadbandController(ModuleController):
    MIN_FREQUENCY = 30.0
    MAX_FREQUENCY = 200.0

    def __init__(self, model):
        super().__init__(model)

    def change_start_frequency(self, value):
        value = float(value)
        if value > self.MIN_FREQUENCY:
            self._model.start_frequency = value
        else:
            self._model_start_frequency = self.MIN_FREQUENCY

    def change_stop_frequency(self, value):
        value = float(value)
        if value < self.MAX_FREQUENCY:
            self._model.stop_frequency = value
        else:
            self._model.stop_frequency = self.MAX_FREQUENCY
