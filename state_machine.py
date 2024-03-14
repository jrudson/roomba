import random
import math
from constants import *
from roomba import *
from utils import Vector2
from roomba import Roomba
from simulation import *

class FiniteStateMachine(object):
    """
    A finite state machine.
    """

    def __init__(self, state):
        self.state = state

    def change_state(self, new_state):
        self.state = new_state

    def update(self, agent):
        self.state.check_transition(agent, self)
        self.state.execute(agent)


class State(object):
    """
    Abstract state class.
    """

    def __init__(self, state_name):
        """
        Creates a state.

        :param state_name: the name of the state.
        :type state_name: str
        """
        self.state_name = state_name

    def check_transition(self, agent, fsm):
        """
        Checks conditions and execute a state transition if needed.

        :param agent: the agent where this state is being executed on.
        :param fsm: finite state machine associated to this state.
        """
        raise NotImplementedError("This method is abstract and must be implemented in derived classes")

    def execute(self, agent):
        """
        Executes the state logic.

        :param agent: the agent where this state is being executed on.
        """
        raise NotImplementedError("This method is abstract and must be implemented in derived classes")


class MoveForwardState(State):
    def __init__(self):
        super().__init__("MoveForward")
        # Todo: add initialization code
        self.linear_speed = FORWARD_SPEED
        self.call_count = 0
        self.time = 0

    def check_transition(self, agent, state_machine):
        # Todo: add logic to check and execute state transition
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        # Verifica se o roomba bateu em uma parede
        get_bumper_state = agent.get_bumper_state()
        if get_bumper_state == True:
            new_state = GoBackState()
            state_machine.change_state(new_state)
        if self.time > MOVE_FORWARD_TIME and get_bumper_state == False:
            new_state = MoveInSpiralState()
            state_machine.change_state(new_state)
        pass

    def execute(self, agent):
        agent.set_velocity(self.linear_speed, 0)
        pass


class MoveInSpiralState(State):
    def __init__(self):
        super().__init__("MoveInSpiral")
        # Todo: add initialization code
        self.linear_speed = FORWARD_SPEED
        self.angular_speed = ANGULAR_SPEED
        self.call_count = 0
        self.radio = 0
        self.time = 0

    def check_transition(self, agent, state_machine):
        # Todo: add logic to check and execute state transition
        get_bumper_state = agent.get_bumper_state()
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        if get_bumper_state == True:
            new_state = GoBackState()
            state_machine.change_state(new_state)
        if self.time > MOVE_IN_SPIRAL_TIME and get_bumper_state == False:
            new_state = MoveForwardState()
            state_machine.change_state(new_state)
        pass

    def execute(self, agent):
        # Todo: add execution logic
        self.radio = INITIAL_RADIUS_SPIRAL + (SPIRAL_FACTOR * self.time)
        angular_speed = ANGULAR_SPEED / self.radio
        agent.set_velocity(self.linear_speed, angular_speed)
        pass


class GoBackState(State):
    def __init__(self):
        super().__init__("GoBack")
        # Todo: add initialization code
        self.linear_speed = BACKWARD_SPEED
        self.time = 0
        self.call_count = 0

    def check_transition(self, agent, state_machine):
        # Todo: add logic to check and execute state transition
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        if self.time > GO_BACK_TIME:
            new_state = RotateState()
            state_machine.change_state(new_state)
        pass

    def execute(self, agent):
        # Todo: add execution logic
        agent.set_velocity(self.linear_speed, 0)
        pass


class RotateState(State):
    def __init__(self):
        super().__init__("Rotate")
        # Todo: add initialization code
        self.time = 0
        self.call_count = 0
        self.random_angular_direction = random.uniform(-1, 1)

    def check_transition(self, agent, state_machine):
        # Todo: add logic to check and execute state transition
        get_bumper_state = agent.get_bumper_state()
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        self.roomba_turning_time = random.uniform(1, MOVE_FORWARD_TIME)
        if get_bumper_state == False and self.time > self.roomba_turning_time:
            new_state = MoveForwardState()
            state_machine.change_state(new_state)
        pass

    def execute(self, agent):
        # Todo: add execution logic
        if self.random_angular_direction > 0:
            agent.set_velocity(0, ANGULAR_SPEED)
        else:
            agent.set_velocity(0, -ANGULAR_SPEED)
        pass
