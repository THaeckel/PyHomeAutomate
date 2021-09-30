"""
Implementation for the state data base for python home automation

Copyright (c) 2021 Timo Haeckel
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from threading import Lock


class StateDataBaseObserver(ABC):
    """
    The StateDataBaseObserver interface declares the update method, used by StateDataBase.
    """
    @abstractmethod
    def stateChangedCallback(self, stateName, stateValue) -> None:
        """ Callback function for changes is the state data baseself.

        This function is registered as a state change callback function 
        at the stateDataBase and is called when ever an obeserved state 
        variable is updated. Overide this method and parse the stateName 
        and stateValue accordingly.   

        Parameters
        ----------
        stateName : str
            The name of the state that is used as a key
        stateValue : complex type
            The value of the state which can be of any complex type    
        """
        pass


class StateDataBase:
    """ A data base for shared state of home automation skills.

    Attributes
    ----------
    states : dict(str, complex type)
        Shared states of home automation skills 
        Key is the name of the state, the value can be of any complex type
    observers : dict(str, list(StateDataBaseObserver))
        Obeservers to be notified on state changes
        Key is the name of the state, the value is a list of StateDataBaseObservers
    mutex : threading.Lock
        Mutex to ensure thread safety for multiple skills accessing the states
    """
    def __init__(self, initialStates=dict()):
        """ 
        Parameters
        ----------
        initialStates : dict(str, complex type) (Default empty dict)
            States that are to be set during initialization in the state data base
            Key is the name of the state, the value can be of any complex type
        """
        self.states = initialStates
        self.observers = dict()
        self.mutex = Lock()

    def getState(self, key):
        """ Get the value of the state with the given key.

        Parameters
        ----------
        key : str
            The name of the state that is used as a key
        
        Returns
        -------
        complex type
            The value of the state which can be of any complex type
            None if the state does not exist
        """
        self.mutex.acquire()
        value = None
        if key in self.states:
            value = self.states[key]
        self.mutex.release()
        return value

    def setState(self, key, value):
        """ Sets the state of key with the given value.
        
        Updates the state with the key in the state data base with the new value
        of stateValue.

        Parameters
        ----------
        key : str
            The name of the state that is used as a key
        value : complex type
            The value of the state to be set which can be of any complex type
        """
        self.mutex.acquire()
        if len(key) > 0:
            self.states[key] = value
            self.notifyObservers(key)
        self.mutex.release()

    def registerObserver(self, key, observer: StateDataBaseObserver):
        """ Register a callbackFct to notify when the state with the key changes.

        The stateChangedCallback of this skill is registered as an observer
        function to be notified if the given state is updated.

        Parameters
        ----------
        key : str
            The name of the state to register a callback for
        observer : StateDataBaseObserver
            The obeserver to be registered for notifications
        """
        if key in self.states:
            if key not in self.observers:
                self.observers[key] = []
            if observer not in self.observers[key]:
                self.observers[key].append(observer)

    def notifyObservers(self, key):
        """ Notifies all registered callbacks that observe the state with the key.

        Calls all callback functions that were registered for a certain key.

        Parameters
        ----------
        key : str
            The name of the state
        """
        if key in self.observers:
            for observer in self.observers[key]:
                observer.stateChangedCallback(key, self.states[key])
