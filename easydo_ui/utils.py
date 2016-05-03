# encoding: utf-8

from easydo_ui import ui
from commands import SelectorMixin


def component_ui(klass):
    setattr(ui, klass.__name__) = klass
    return klass

def componet_commands(name):

    def _commands(klass):
        SelectorMixin.components[name] = klass
        return klass

    return _commands 
