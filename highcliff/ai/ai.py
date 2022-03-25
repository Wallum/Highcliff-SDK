__author__ = "Jerry Overton"
__copyright__ = "Copyright (C) 2020 appliedAIstudio"
__version__ = "0.1"

# copying the state of the world for reflection
import copy

from highcliff.actions.actions import ActionStatus

# AI, GOAP
from goap.planner import RegressivePlanner
from goap.algo.astar import PathNotFoundException

# used to create and access centralized infrastructure
from highcliff.infrastructure import LocalNetwork, MqttNetwork

# used to make AI a singleton
from highcliff.singleton import Singleton


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
    __network = LocalNetwork.instance()
    __goals = None
    __capabilities = []
    __diary = []

    def network(self):
        return self.__network

    def connect(self, endpoint="a15645u9kev0b1-ats.iot.eu-west-2.amazonaws.com",
                port=8883, cert="/home/ubuntu/certs/certificate.pem.crt",
                key="/home/ubuntu/certs/private.pem.key",
                topic='#'):
        self.__network = MqttNetwork.instance()
        self.__network.connect(endpoint, port, cert, key, topic)

    def set_goals(self, goals):
        self.__goals = goals

    def capabilities(self):
        return self.__capabilities

    def add_capability(self, action):
        self.__capabilities.append(action)

    def run(self, life_span_in_iterations):
        # if the life span is specified as some positive number, stay alive for that number of iterations
        if life_span_in_iterations > 0:
            for iteration in range(life_span_in_iterations):
                self.__run_ai()
        # if the life span is specified as -1, run forever
        else:
            while True:
                self.__run_ai()

    def reset(self):
        self.__network.reset()
        self.__goals = None
        self.__diary = []
        self.__capabilities = []

    def __get_world_state(self):
        # this function returns the current state of the world
        return self.__network.the_world()

    def __select_goal(self, prioritized_goals):
        # work on the next highest-priority goal that has not yet been met

        # the default is to select an empty goal
        selected_goal = {}

        # go through goals in priority order
        for goal in self.__goals:
            # if the condition is not in the world, add it to the world, assume it's false, pursue the goal
            if goal not in self.__get_world_state():
                self.__network.update_the_world({goal: False})
                selected_goal = {goal: self.__goals[goal]}
                break

            # if the goal is already met (matches the condition of the world) then skip it
            if self.__goals[goal] == self.__get_world_state()[goal]:
                pass

            # if the goal is not met (mismatches the condition of the world) pursue it
            if self.__goals[goal] != self.__get_world_state()[goal]:
                selected_goal = {goal: self.__goals[goal]}
                break

        return selected_goal

    def __reflect(self, goal, world_state_before, plan, action_status, world_state_after):
        diary_entry = {
            "my_goal": goal,
            "the_world_state_before": world_state_before,
            "my_plan": plan,
            "action_status": action_status,
            "the_world_state_after": world_state_after
        }
        self.__diary.append(diary_entry)

    def __run_ai(self):
        # todo: go through this and get rid of unnecessary updates
        # select a single goal from the list of goals
        goal = self.__select_goal(self.__goals)

        # create a plan to achieve the selected goal
        planner = RegressivePlanner(self.__get_world_state(), self.capabilities())

        # start by assuming that there is no plan, the action will have no effect and will fail
        plan = None
        action_status = ActionStatus.FAIL
        actual_effect = {}

        # take a snapshot of the current world state before taking action that may change it
        world_state_snapshot = copy.copy(self.__get_world_state())

        try:
            # make a plan
            plan = planner.find_plan(goal)

            try:
                next_action = plan[0].action

                # execute the first act in the plan. it will affect the world and get us one step closer to the goal
                # the plan will be updated and actions executed until the goal is reached
                intended_effect = copy.copy(next_action.effects)
                next_action.act()

            except IndexError:
                # if there is no viable plan, then record no intended effect
                intended_effect = {}

            # the action is a success if the altered world matches the action's intended effect
            actual_effect = copy.copy(self.__get_world_state())
            action_had_intended_effect = intent_is_real(intended_effect, actual_effect)
            if action_had_intended_effect:
                action_status = ActionStatus.SUCCESS

        except PathNotFoundException:
            # no viable plan found. no action to be taken
            pass

        except KeyError:
            # there are no registered actions that can satisfy the specified goal. no action to be taken
            pass

        # record the results of this iteration
        # todo: replace the 'after' world state with a copy
        self.__reflect(copy.copy(goal), world_state_snapshot, copy.copy(plan), copy.copy(action_status), copy.copy(self.__get_world_state()))

    def diary(self):
        return self.__diary
