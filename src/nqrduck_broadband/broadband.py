from PyQt5.QtCore import pyqtSignal, QObject
from nqrduck.module.module import Module
from nqrduck_broadband.broadband_model import BroadbandModel
from nqrduck_broadband.broadband_view import BroadbandView
from nqrduck_broadband.broadband_controller import BroadbandController
from nqrduck_broadband.broadband_widget import Ui_Form

Broadband = Module(BroadbandModel, BroadbandController, BroadbandView)
