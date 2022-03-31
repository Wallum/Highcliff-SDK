import unittest

# needed to test local infrastructure
from infrastructure import LocalNetwork


class TestInfrastructure(unittest.TestCase):
    def test_local_infrastructure_reset(self):

        local_network = LocalNetwork.instance()

        # add state to the world and check that the world is not empty
        dummy_state = {'dummy_state': True}
        local_network.update_the_world(dummy_state)
        world_is_not_empty = len(local_network.the_world()) > 0
        self.assertTrue(world_is_not_empty)

        # add a topic and check that the topics are not empty
        dummy_topic = "dummy_topic"
        local_network.create_topic(dummy_topic)
        topics_are_not_empty = len(local_network.topics()) > 0
        self.assertTrue(topics_are_not_empty)

        # reset the network infrastructure
        local_network.reset()

        # check that the world state has been reset
        reset_world = {}
        self.assertEqual(reset_world, local_network.the_world())

        # check that the topics have been reset
        reset_topics = []
        self.assertEqual(reset_topics, local_network.topics())

    def test_local_infrastructure(self):

        # create two instances of local networks
        first_local_network = LocalNetwork.instance()
        second_local_network = LocalNetwork.instance()

        # the network instances should be the same
        self.assertTrue(first_local_network is second_local_network)

        # the world in both networks should initially be empty
        expected_world = {}
        self.assertEqual(expected_world, first_local_network.the_world())
        self.assertEqual(expected_world, second_local_network.the_world())

        # update the world in the first network and check for the same update in the second network
        world_update = {'world_updated': True}
        first_local_network.update_the_world(world_update)
        self.assertEqual(world_update, first_local_network.the_world())
        self.assertEqual(world_update, second_local_network.the_world())

        # the topics in both networks should initially be empty
        expected_topics = []
        self.assertEqual(expected_topics, first_local_network.topics())
        self.assertEqual(expected_topics, second_local_network.topics())

        # update the topics in the first network and check for the same update in the second network
        topic = "dummy_topic"
        topic_list = [topic]
        first_local_network.create_topic(topic)
        self.assertEqual(topic_list, first_local_network.topics())
        self.assertEqual(topic_list, second_local_network.topics())


if __name__ == '__main__':
    unittest.main()
