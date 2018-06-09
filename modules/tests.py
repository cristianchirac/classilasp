import unittest
import state
import utils

class TestStringMethods(unittest.TestCase):

    def testInitProgressBar(self):
        utils.initProgressBar()
        self.assertEqual(state.get('iterationNum'), 0)

    def testSetParamsFromArgs(self):
        utils.setParamsFromArgs(['-p', '-n'])
        self.assertEqual(state.get('prenamedComponents'), True)
        self.assertEqual(state.get('noise'), True)

    def testCheckListsHaveSameElements(self):
        l1 = [2, 3, 1, 2]
        l2 = [1, 2, 2, 3]
        self.assertEqual(utils.checkListsHaveSameElements(l1, l2), True)

    def testCheckListsDontHaveSameElements1(self):
        l1 = [2, 3, 1, 3]
        l2 = [1, 2, 2, 3]
        self.assertEqual(utils.checkListsHaveSameElements(l1, l2), False)

    def testCheckListsDontHaveSameElements2(self):
        l1 = [2, 3, 1]
        l2 = [1, 2, 2, 3]
        self.assertEqual(utils.checkListsHaveSameElements(l1, l2), False)

    def testGetArgsFromPred(self):
        args = utils.getArgsFromPred("pred(arg1,arg2,arg3).")
        self.assertEqual(args, ["arg1", "arg2", "arg3"])

    def testGetModelId(self):
        mId = utils.getModelId("model(m123).")
        self.assertEqual(mId, "m123")

    def testGetNodeIdFromNodePred(self):
        nId = utils.getNodeIdFromNodePred("node(m123,n789,ice).")
        self.assertEqual(nId, "n789")

    def testGetNodeTypeFromNodePred(self):
        nT = utils.getNodeTypeFromNodePred("node(m123,n789,ice).")
        self.assertEqual(nT, "ice")

    def testGetEdge(self):
        edge = utils.getEdge("edge(18,c1,pr18_2_0,pr18_15_1)")
        self.assertEqual(edge, "(pr18_2_0,pr18_15_1)")

    def testListAsEnumeratedString(self):
        l = utils.listAsEnumeratedString(['a', 'b', 'c'])
        self.assertEqual(l, "a, b, c")        

if __name__ == '__main__':
    unittest.main()