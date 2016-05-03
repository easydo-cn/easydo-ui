# encoding: utf-8

import ui
from commands import SelectorMixin


def component_ui(klass):
    setattr(ui, klass.__name__, klass)
    return klass

def component_commands(name):

    def _commands(klass):
        SelectorMixin.components[name] = klass
        return klass

    return _commands 
