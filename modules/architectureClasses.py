import utils

class Port(object):
 
    def __init__(self, portId, portType, direction):
        self.portId = portId.lower()
        self.portType = portType
        self.direction = direction
 
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return 	self.portType == other.portType and self.direction == other.direction
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
    	return '(' + str(self.portId) + ',' + str(self.portType) + ',' + str(self.direction) + ')'

    def isUsedInModel(self, edges):
    	for edge in edges:
    		portAId = edge.getPortAId()
    		portBId = edge.getPortBId()
    		if (self.portId == portAId or self.portId == portBId):
    			return True
    	return False

class Edge(object):
 
    def __init__(self, ports):
        self.ports = ports.lower()

    def __str__(self):
    	return str(self.ports)

    def getPortAId(self):
    	strRepr = str(self.ports)
    	i1 = strRepr.index('(')
    	i2 = strRepr.index(',')
    	return strRepr[i1 + 1 : i2]

    def getPortBId(self):
    	strRepr = str(self.ports)
    	i1 = strRepr.index(',')
    	i2 = strRepr.index(')')
    	return strRepr[i1 + 1 : i2]

class PortGroup(object):
 
    def __init__(self, groupId, ports):
        self.groupId = groupId
        self.ports = ports
 
    def __eq__(self, other):
        if isinstance(other, self.__class__):
        	return utils.checkListsHaveSameElements(self.ports, other.ports)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
    	return str(list(map(str, self.ports)))

    def isUsedInModel(self, edges):
    	for port in self.ports:
    		if (port.isUsedInModel(edges)):
    			return True
    	return False

class Component(object):
 
    def __init__(self, compId, groups):
    	self.compId = compId.lower()
    	self.groups = groups
    	self.name   = None
 
    def __eq__(self, other):
        if isinstance(other, self.__class__):
        	return utils.checkListsHaveSameElements(self.groups, other.groups)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
    	groupsStr = str(list(map(str, self.groups)))
    	if (self.name):
    		return '(' + str(self.name) + ', ' + groupsStr + ')'
    	else:
    		return groupsStr

    def isUsedInModel(self, edges):
    	for group in self.groups:
    		if (group.isUsedInModel(edges)):
    			return True
    	return False

class Model(object):
 
    def __init__(self, modelId, components, edges):
        self.modelId    = modelId
        self.components = components
        self.edges      = edges
        self.labels     = list()

    def __str__(self):
    	return ('Model ' + self.modelId +':\n\n' +
                'Components:\n' +
    			str(list(map(str, self.components))) +
    			'\nEdges:\n' +
    			str(list(map(str, self.edges))) + '\n')

    def usesComponent(self, comp):
    	return comp.isUsedInModel(self.edges)

    def getUsedComponents(self):
    	usedComps = list()
    	for comp in self.components:
    		if (comp.isUsedInModel(self.edges)):
    			usedComps.append(comp)
    	return usedComps

    def updateLabels(self, labels):
        self.labels = labels