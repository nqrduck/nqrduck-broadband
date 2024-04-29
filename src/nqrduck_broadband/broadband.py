"""Module creation for the Broadband module."""
from nqrduck.module.module import Module
from .model import BroadbandModel
from .view import BroadbandView
from .controller import BroadbandController

Broadband = Module(BroadbandModel, BroadbandView, BroadbandController)
