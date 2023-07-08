from PyQt6.QtCore import pyqtSignal, QObject
from nqrduck.module.module import Module
from nqrduck_broadband.model import BroadbandModel
from nqrduck_broadband.view import BroadbandView
from nqrduck_broadband.controller import BroadbandController
from nqrduck_broadband.widget import Ui_Form

Broadband = Module(BroadbandModel, BroadbandView, BroadbandController)
