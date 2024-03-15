from enum import Enum
from constants import *
import random


class ExecutionStatus(Enum):
    """
    Represents the execution status of a behavior tree node.
    """
    SUCCESS = 0
    FAILURE = 1
    RUNNING = 2


class BehaviorTree(object):
    """
    Represents a behavior tree.
    """
    def __init__(self, root=None):
        """
        Creates a behavior tree.

        :param root: the behavior tree's root node.
        :type root: TreeNode
        """
        self.root = root

    def update(self, agent):
        """
        Updates the behavior tree.

        :param agent: the agent this behavior tree is being executed on.
        """
        if self.root is not None:
            self.root.execute(agent)


class TreeNode(object):
    """
    Represents a node of a behavior tree.
    """
    def __init__(self, node_name):
        """
        Creates a node of a behavior tree.

        :param node_name: the name of the node.
        """
        self.node_name = node_name
        self.parent = None

    def enter(self, agent):
        """
        This method is executed when this node is entered.

        :param agent: the agent this node is being executed on.
        """
        raise NotImplementedError("This method is abstract and must be implemented in derived classes")

    def execute(self, agent):
        """
        Executes the behavior tree node logic.

        :param agent: the agent this node is being executed on.
        :return: node status (success, failure or running)
        :rtype: ExecutionStatus
        """
        raise NotImplementedError("This method is abstract and must be implemented in derived classes")


class LeafNode(TreeNode):
    """
    Represents a leaf node of a behavior tree.
    """
    def __init__(self, node_name):
        super().__init__(node_name)


class CompositeNode(TreeNode):
    """
    Represents a composite node of a behavior tree.
    """
    def __init__(self, node_name):
        super().__init__(node_name)
        self.children = []

    def add_child(self, child):
        """
        Adds a child to this composite node.

        :param child: child to be added to this node.
        :type child: TreeNode
        """
        child.parent = self
        self.children.append(child)


class SequenceNode(CompositeNode):
    """
    Represents a sequence node of a behavior tree.
    """
    def __init__(self, node_name):
        super().__init__(node_name)
        # We need to keep track of the last running child when resuming the tree execution
        self.running_child = None

    def enter(self, agent):
        # When this node is entered, no child should be running
        self.running_child = None

    def execute(self, agent):
        if self.running_child is None:
            # If a child was not running, then the node puts its first child to run
            self.running_child = self.children[0]
            self.running_child.enter(agent)
        loop = True
        while loop:
            # Execute the running child
            status = self.running_child.execute(agent)
            if status == ExecutionStatus.FAILURE:
                # This is a sequence node, so any failure results in the node failing
                self.running_child = None
                return ExecutionStatus.FAILURE
            elif status == ExecutionStatus.RUNNING:
                # If the child is still running, then this node is also running
                return ExecutionStatus.RUNNING
            elif status == ExecutionStatus.SUCCESS:
                # If the child returned success, then we need to run the next child or declare success
                # if this was the last child
                index = self.children.index(self.running_child)
                if index + 1 < len(self.children):
                    self.running_child = self.children[index + 1]
                    self.running_child.enter(agent)
                else:
                    self.running_child = None
                    return ExecutionStatus.SUCCESS


class SelectorNode(CompositeNode):
    """
    Represents a selector node of a behavior tree.
    """
    def __init__(self, node_name):
        super().__init__(node_name)
        # We need to keep track of the last running child when resuming the tree execution
        self.running_child = None

    def enter(self, agent):
        # When this node is entered, no child should be running
        self.running_child = None

    def execute(self, agent):
        if self.running_child is None:
            # If a child was not running, then the node puts its first child to run
            self.running_child = self.children[0]
            self.running_child.enter(agent)
        loop = True
        while loop:
            # Execute the running child
            status = self.running_child.execute(agent)
            if status == ExecutionStatus.FAILURE:
                # This is a selector node, so if the current node failed, we have to try the next one.
                # If there is no child left, then all children failed and the node must declare failure.
                index = self.children.index(self.running_child)
                if index + 1 < len(self.children):
                    self.running_child = self.children[index + 1]
                    self.running_child.enter(agent)
                else:
                    self.running_child = None
                    return ExecutionStatus.FAILURE
            elif status == ExecutionStatus.RUNNING:
                # If the child is still running, then this node is also running
                return ExecutionStatus.RUNNING
            elif status == ExecutionStatus.SUCCESS:
                # If any child returns success, then this node must also declare success
                self.running_child = None
                return ExecutionStatus.SUCCESS


class RoombaBehaviorTree(BehaviorTree):
    """
    Represents a behavior tree of a roomba cleaning robot.
    """
    def __init__(self):
        super().__init__()
        # Todo: construct the tree here
        # Constructing the tree
        root_node = SelectorNode("Root")
        sequence_one = SequenceNode("SequenceOne")
        sequence_two = SequenceNode("SequenceTwo")

        # Creating and adding nodes to the tree
        move_forward_node = MoveForwardNode()
        move_in_spiral_node = MoveInSpiralNode()
        go_back_node = GoBackNode()
        rotate_node = RotateNode()

        # Adding nodes to the root selector node
        sequence_one.add_child(move_forward_node)
        sequence_one.add_child(move_in_spiral_node)
        sequence_two.add_child(go_back_node)
        sequence_two.add_child(rotate_node)

        root_node.add_child(sequence_one)
        root_node.add_child(sequence_two)

        # Setting the root node of the behavior tree
        self.root = root_node

class MoveForwardNode(LeafNode):
    def __init__(self):
        super().__init__("MoveForward")
        # Todo: add initialization code
        self.linear_speed = FORWARD_SPEED

    def enter(self, agent):
        # Todo: add enter logic
        self.call_count = 0
        pass

    def execute(self, agent):
        # Todo: add execution logic
        get_bumper_state = agent.get_bumper_state()
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        if self.time < 3:
            if get_bumper_state == False:
                agent.set_velocity(self.linear_speed, 0)
                return ExecutionStatus.RUNNING
            else:
                return ExecutionStatus.FAILURE
        else:
            return ExecutionStatus.SUCCESS
        pass


class MoveInSpiralNode(LeafNode):
    def __init__(self):
        super().__init__("MoveInSpiral")
        # Todo: add initialization code
        self.angular_speed = ANGULAR_SPEED
        self.linear_speed = FORWARD_SPEED

    def enter(self, agent):
        # Todo: add enter logic
        self.call_count = 0
        pass

    def execute(self, agent):
        # Todo: add execution logic
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        self.radio = INITIAL_RADIUS_SPIRAL + (SPIRAL_FACTOR * self.time)
        angular_speed = ANGULAR_SPEED / self.radio
        get_bumper_state = agent.get_bumper_state()
        if self.time < 20:
            if get_bumper_state == False:
                agent.set_velocity(self.linear_speed, angular_speed)
                test = ExecutionStatus.RUNNING
            else:
                test = ExecutionStatus.FAILURE
            return test
        else:
            return ExecutionStatus.SUCCESS
        pass


class GoBackNode(LeafNode):
    def __init__(self):
        super().__init__("GoBack")
        # Todo: add initialization code
        self.linear_speed = FORWARD_SPEED
        self.call_count = 0

    def enter(self, agent):
        # Todo: add enter logic
        pass

    def execute(self, agent):
        # Todo: add execution logic
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        get_bumper_state = agent.get_bumper_state()

        if self.time > GO_BACK_TIME and get_bumper_state == False:
            return ExecutionStatus.SUCCESS
        else:
            agent.set_velocity(BACKWARD_SPEED, 0)
            return ExecutionStatus.RUNNING
        pass


class RotateNode(LeafNode):
    def __init__(self):
        super().__init__("Rotate")
        # Todo: add initialization code

    def enter(self, agent):
        # Todo: add enter logic
        self.call_count = 0
        self.random_angular_direction = random.uniform(-1, 1)
        self.roomba_turning_time = random.uniform(1, MOVE_FORWARD_TIME)
        pass

    def execute(self, agent):
        # Todo: add execution logic
        self.call_count += 1
        self.time = self.call_count * SAMPLE_TIME
        get_bumper_state = agent.get_bumper_state()
        if self.time < self.roomba_turning_time:
            if self.random_angular_direction > 0:
                agent.set_velocity(0, ANGULAR_SPEED)
                return ExecutionStatus.RUNNING
            else:
                agent.set_velocity(0, -ANGULAR_SPEED)
                return ExecutionStatus.RUNNING
        elif get_bumper_state == False:
            return ExecutionStatus.FAILURE
        pass

