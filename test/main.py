from tkinter import *
import tkinter as tk
import A
import B
import dependency_injector.containers as containers
import dependency_injector.providers as providers
from Container import *

class Observer():
    _observers = []
    def __init__(self):
        self._observers.append(self)
        self._observables = {}
    def observe(self, event_name, callback):
        self._observables[event_name] = callback


class Event():
    def __init__(self, name, data, autofire = True):
        self.name = name
        self.data = data
        if autofire:
            self.fire()
    def fire(self):
        for observer in Observer._observers:
            if self.name in observer._observables:
                observer._observables[self.name](self.data)

def main():

    frame = Tk()
    a = A.A(frame)
    b = B.B(frame)
    frame.mainloop()


if __name__ == '__main__':
    main()
