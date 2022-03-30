# SDK-Python
Python version of a microservice Software Development Kit (SDK) for the Highcliff intelligent environment system

## Overview

The goal of this project is to speed the development of an intelligent, automomous environment that looks after the well being of the severly disabled. The environment should constantly monitor, anticipate and adapt itself to the person's changing needs. It should be easy for people and things in the environment to communicate.

The intended technical environment is a network of people and smart things collaborating using a central message queue. Every smart thing participating in the network must be capable of publishing and subscribing to a central message queue. Smart things must use messages to and from the queue to coordinate their actions. Each smart thing must be capable of making itself known to other participants in the network. They must also be capable of reading and contributing to the collective state of the network-- a shared world view. Every smart thing must be capable of taking action, communicating the success or failure of the action, and updating the shared world view based on the outcome of that acton.

The SDK provides (and hides from smart-thing developers) the infrastructure integration required of all smart things. The SDK provides developers an interface for publishing and subscribing to a central message queue. The SDK provides framework classes for smart-thing developers to build custom actions. The SDK (specifically, the AI known as Highcliff) determines when to call custom actions. The SDK handles registering smart things and making them known in the network. It handles reading and updating the shared world view. With the SDK, the smart thing developer need only include the appropriate SDK classes and implement the appropriate custom behavior.

### Using the SDK
The SDK provides a set of classes that makes it easier for developers to publish messages, subscribe to topics, and read from topics. These classes hide the details required to coordinate with a central message queue. The SDK makes it possible to swap out network participants and underlying message infrastructure without affecting smart-thing development. All messages are validated against a central schema. The Highcliff AI monitors and reacts (depending on the content) to messages published.

The SDK also provides a set of classes that represent all meaningful actions that can be taken by smart things in the network. Every meaningful action that can be taken by a smart thing has (or should have) a corresponding SDK class. A smart thing participates in the network by implementing action classes. Specifically, the developer implements custom behavior of the action class. As part of the SDK, the acton class tells the AI the intended effect of the action and the preconditions for executing the action. The AI uses this information to organize actions into plans for accomplishing goals.

### The Highcliff AI
Highcliff is the artificial intelligence that provides communication and intelligent orchestration of every smart thing in the network. Highcliff's AI is based on Goal-Oriented Action Programming (GOAP). GOAP is a technique often applied to providing intelligent behavior to non-player characters in video games. Being based on GOAP, Highcliff's AI is goal-driven, rather than data driven. Highcliff's intelligence comes from its ability to organize dynamic lists of actions into plans that achieve goals, rather than its ability to learn from large data sets.

Highcliff is given a static set of goals designed to maintain a person's wellbeing. Highcliff percieves the environment, decides which of its goals are not met, and chooses a goal to pursue. Highcliff reasons about its goal and organizes its available resources into a plan. Highcliff acts on its plan, monitors the results of his actions and reflects (using a diary) on the entire process.


## Quick Start
1. Install Python
2. Clone this repository
3. Run `\examples\smart_thing_quick_start.py`
4. You should see the following output:
```
We are now monitoring body temperature
```

### The Complete Quick Start Code

```python
# needed to run a local version of the AI
from highcliff.ai import AI

# the Highcliff actions to be tested
from highcliff.exampleactions import MonitorBodyTemperature

# get a reference to the ai and its network
highcliff = AI.instance()
network = highcliff.network()


# execute a single action with a single goal:

# define a test body temperature monitor
class TestBodyTemperatureMonitor(MonitorBodyTemperature):
  def behavior(self):
    print("We are now monitoring body temperature")


# instantiate the test body temperature monitor
TestBodyTemperatureMonitor(highcliff)

# define the test world state and goals
network.update_the_world({})

# run a local version of Highcliff
highcliff.set_goals({"is_room_temperature_change_needed": True})
highcliff.act(life_span_in_iterations=1)

```

### Explaining the Quick Start

To use this SDK and run your solution on your local machine, start by importing the Highcliff AI and the specific Highcliff action you intend to implement.

```python
# needed to run a local version of the AI
from highcliff.ai import AI

# the Highcliff actions to be tested
from highcliff.exampleactions import MonitorBodyTemperature
```

Create a reference to the artificial intelligence. Use the AI to get a reference to its underlying infrastructure.

```python
# get a reference to the ai and its network
highcliff = AI.instance()
network = highcliff.network()
```

Write the custom behavior for any action that you imported.

```python
class TestBodyTemperatureMonitor(MonitorBodyTemperature):
    def behavior(self):
        print("We are now monitoring body temperature")
```

Instantiate your new action. Be sure to pass the new action a reference to the AI that will be controlling the action.

```python
TestBodyTemperatureMonitor(highcliff)
```

Use the infrastructure reference to define the current state of the world. In the quick start example, we started with an empty world `{}`. Set goals for the AI. Run the AI. As part of the AI run, specify the number of iterations the AI is to run before terminating.

```python
# define the test world state and goals
network.update_the_world({})

# run a local version of Highcliff
highcliff.set_goals({"is_room_temperature_change_needed": True})
highcliff.act(life_span_in_iterations=1)
```

The AI will select a goal, create a plan, and (if properly configured) select and run your action. You should see the custom behavior you specified running locally.

```
We are now monitoring body temperature
```

## More Examples
### Other Quick Starts
* `ai_quick_start` provides an example of how to run an instance of the artificial intelligence engine
* `pubsub_quick_start` provides an example of how to use the infrastructure to publsih and subscribe to messages
* `smart_thing_in_depth` provides an example of to use the ai with multiple actions

## Roadmap

- [ ] Release the beta Python version
- [ ] Integrate beta Python version with AWS CMD Reference Cut Down Architecture
- [ ] Test the beta Python version in a full hackathon
- [ ] Release version 1
- [ ] Release versions in other languages
  - [ ] c#
  - [ ] node.js
