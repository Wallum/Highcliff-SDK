__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2022 appliedAIstudio LLC"
__version__ = "0.0.1"

# copying the state of the world for reflection
import copy
import time

from highcliff.actions.actions import ActionStatus

# AI, GOAP
from goap.planner import RegressivePlanner
from goap.algo.astar import PathNotFoundException

# used to create and access centralized infrastructure
from infrastructure import LocalNetwork, AiMqttNetwork

# used to make AI a singleton
from highcliff.singleton import Singleton

# needed to log debug messages to the terminal window
from highcliff.logging import log_event_to_the_terminal_window


def intent_is_real(intent, reality):
    is_real = True
    for key in intent:
        try:
            if intent[key] != reality[key]:
                # there is a value in the intent not in reality
                is_real = False
        except KeyError:
            # there is a key in the intent not in reality
            is_real = False

    return is_real


@Singleton
class AI:
    _network = LocalNetwork.instance()
    _goals = None
    _capabilities = []
    _diary = []
    _debug_logging = False

    def set_debug_logging(self, debug_logging):
        self._debug_logging = debug_logging

    def network(self):
        return self._network

    def connect(self, endpoint="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
                port=8883, cert="/home/ubuntu/certs/certificate.pem.crt",
                key="/home/ubuntu/certs/private.pem.key"):
        """Replace local network, which is default, with mqtt network, and connect to it"""
        self.__network = AiMqttNetwork.instance()
        self.__network.connect(endpoint, port, cert, key)

    def set_goals(self, goals):
        self._goals = goals

    def capabilities(self):
        return self._capabilities

    def add_capability(self, action):
        self._capabilities.append(action)

        # log the registration of the action
        if self._debug_logging:
            log_event_to_the_terminal_window("Registered an action " +
                                             str(action) + " with effects " + str(action.effects))

    # TODO: add code to remove a capability

    def run(self, life_span_in_iterations):
        seconds_to_pause_between_ai_runs = 2

        # if the life span is specified as some positive number, stay alive for that number of iterations
        if life_span_in_iterations > 0:
            self._run_temporarily(life_span_in_iterations, seconds_to_pause_between_ai_runs)

        # if the life span is specified as -1, run forever
        else:
            self._run_indefinitely(seconds_to_pause_between_ai_runs)

    def _run_indefinitely(self, seconds_to_pause_between_ai_runs):
        # log that the ai is running
        if self._debug_logging:
            log_event_to_the_terminal_window("Running the AI indefinitely")
        # run the ai
        while True:
            self._run_ai()
            # pause to allow for processing in other areas of the ai
            time.sleep(seconds_to_pause_between_ai_runs)

    def _run_temporarily(self, life_span_in_iterations, seconds_to_pause_between_ai_runs):
        # log that the ai is running
        if self._debug_logging:
            log_event_to_the_terminal_window("Running the AI for " + str(life_span_in_iterations) + " iterations")
        # run the ai
        for iteration in range(life_span_in_iterations):
            self._run_ai()
            # pause to allow for processing in other areas of the ai
            time.sleep(seconds_to_pause_between_ai_runs)

    def reset(self):
        self._network.reset()
        self._goals = None
        self._diary = []
        self._capabilities = []

    def _get_world_state(self):
        # this function returns the current state of the world
        return self._network.the_world()

    def _select_goal(self, prioritized_goals):
        # work on the next highest-priority goal that has not yet been met

        # the default is to select an empty goal
        selected_goal = {}

        # go through goals in priority order
        for goal in self._goals:
            # if the condition is not in the world, add it to the world, assume the goal is not met, pursue the goal
            if goal not in self._get_world_state():
                goal_not_met = not self._goals[goal]
                self._network.update_the_world({goal: goal_not_met})
                selected_goal = {goal: self._goals[goal]}
                break

            # if the goal is already met (matches the condition of the world) then skip it
            if self._goals[goal] == self._get_world_state()[goal]:
                pass

            # if the goal is not met (mismatches the condition of the world) pursue it
            if self._goals[goal] != self._get_world_state()[goal]:
                selected_goal = {goal: self._goals[goal]}
                break

        return selected_goal

    def _reflect(self, goal, world_state_before, plan, action_status, world_state_after):
        diary_entry = {
            "my_goal": goal,
            "the_world_state_before": world_state_before,
            "my_plan": plan,
            "action_status": action_status,
            "the_world_state_after": world_state_after
        }
        self._diary.append(diary_entry)

    def _plan(self, goal):
        # create a planner capable of achieving the selected goal
        planner = RegressivePlanner(self._get_world_state(), self.capabilities())
        plan = None

        try:
            # make a plan
            plan = planner.find_plan(goal)

            # log that a plan has been created
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI has made a plan to execute the goal")

        except PathNotFoundException:
            # no viable plan found. no action to be taken

            # log that no viable plan was found
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI has found no viable plan to achieve the selected goal")

        except KeyError:
            # there are no registered actions that can satisfy the specified goal. no action to be taken

            # log that no necessary registered actions were found
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI has no registered actions capable of satisfying the goal")

        return plan

    def _act(self, plan):
        try:
            next_action = plan[0].action

            # execute the first act in the plan. it will affect the world and get us one step closer to the goal
            # the plan will be updated and actions executed until the goal is reached
            intended_effect = copy.copy(next_action.effects)
            next_action.act(self.network())

            # log that the ai has taken an action
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI has taken an action")

            # TODO: catch the error if the action is no longer available

        except IndexError:
            # if the given plan has no actions, then record no intended effect
            intended_effect = {}

            # log that the ai's plan has no actions
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI's plan has no actions to execute")

        except TypeError:
            # if there is no viable plan, then record no intended effect
            intended_effect = {}

            # log that the ai could not find a viable plan
            if self._debug_logging:
                log_event_to_the_terminal_window("The AI could not find a viable plan")

        return intended_effect

    def _run_ai(self):
        # select a single goal from the list of goals
        goal = self._select_goal(self._goals)

        # log that a goal has been selected
        if self._debug_logging:
            log_event_to_the_terminal_window("The AI has selected a goal: " + str(goal))

        # start by assuming that there is no plan, the action will have no effect and will fail
        action_status = ActionStatus.FAIL

        # take a snapshot of the current world state before taking action that may change it
        world_state_snapshot = copy.copy(self._get_world_state())

        # make a plan
        plan = self._plan(goal)

        # execute the first act in the plan. it will affect the world and get us one step closer to the goal
        # the plan will be updated and actions executed until the goal is reached
        intended_effect = self._act(plan)

        # the action is a success if the altered world matches the action's intended effect
        actual_effect = copy.copy(self._get_world_state())
        action_had_intended_effect = intent_is_real(intended_effect, actual_effect)
        if action_had_intended_effect:
            action_status = ActionStatus.SUCCESS

        # record the results of this iteration
        self._reflect(copy.copy(goal), world_state_snapshot, copy.copy(plan), copy.copy(action_status), copy.copy(self._get_world_state()))

    def diary(self):
        return self._diary
