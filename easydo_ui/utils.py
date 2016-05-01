# encoding: utf-8
from easydo_ui import ui


def ui_component(klass):
    setattr(ui, klass.__name__) = klass

