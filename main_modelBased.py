# Overview:
'''
 Develop a randomized policy (choose direction randomly)
 -- Effectively acheived by setting random values
 Calculate consistent state values for this policy.
 Develop a new policy that is greedy with respect to these state values.
 Loop.
 Each policy is guaranteed to be a strict improvement over the previous,
 except in the case in which the optimal policy has already been found.
'''
# We assume that we know the transition function
# -- Given state, action, we can determine the next state
# -- Later we want to relax this assumption (use probabilities)
# We assume that we know the reward function

import numpy as np

# Input: state variables
# Output: value of state
def createValNetwork(dimState, numHidden):
    # Build a feed forward neural network (with one hidden layer)
    from pybrain.structure import SigmoidLayer, LinearLayer
    from pybrain.tools.shortcuts import buildNetwork
    valNet = buildNetwork(dimState, # Number of input units
                       numHidden,   # Number of hidden units 
                       1, 	        # Number of output units
                       bias = True,
                       hiddenclass = SigmoidLayer,
                       outclass = LinearLayer # Allows for a large output
                       )	
    return valNet

# Input: state variables
# Output: classification of actions (one hot encoded)
def createPolNetwork(dimState, numHidden, numAct):
     # Build a feed forward neural network (with a single hidden layer)
    from pybrain.structure import SigmoidLayer, SoftmaxLayer
    from pybrain.tools.shortcuts import buildNetwork
    polNet = buildNetwork(dimState, # Number of input units
                       numHidden, 	# Number of hidden units
                       numAct, 	        # Number of output units
                       bias = True,
                       hiddenclass = SigmoidLayer,
                       outclass=SoftmaxLayer # Outputs are in (0,1), and add to 1
                       )	
    return polNet

# Uses only one state variable (old code)    
def mainModelBased1D():
    # 1. Create a random value function
    dimState = 1 # Number of state variables
    numHiddenVal = 20 # Number of hidden neurons
    valNet = createValNetwork(dimState,numHiddenVal)  # Using two hidden layers for precision  
    
    # 2. Create a random policy network
    numHiddenPol = 20 # Number of hidden neurons
    numAct = 10 # Number of actions
    polNet = createPolNetwork(dimState, numHiddenPol, numAct)       
    
    
    # 3. Update values based on current policy
    # The policy is greedy with respect to the value estimates
    
    # 3a. Determine subset of state to update on
    # It isn't practical to visit every possible state
    # Instead, we will work on a discretized version of the state space, and trust to the neural network for interpolation    
    # Here we set the states used to update the policy
    start = 0
    stop = 10    
    policyEvalStates = np.linspace(start, stop, num=10) # Will need to be extended for more state variables
    
    # Print initial policy
    print('Initial policy:')
    for state in policyEvalStates:
        print(np.argmax(polNet.activate([state])))       
    
    # Make values consistent with policy
    import evalPolicy
    vMaxAll = 0.5 # We require values to stop changing by any more than this amount before we return the updated values
    stepSize = 0.5 # How far the airplane moves each time (needed to predict next state)
    thermRadius = 3 # Standard deviation of normal shaped thermal   
    
    numLearn = 3 # Number of times to repaet learning cycle
    
    for i in range(numLearn):
        import modelBased1D as mb1
        valNet = mb1.evalPolicy1D(valNet,polNet,policyEvalStates,vMaxAll, stepSize, thermRadius)
        
        # Print new value network on selected points
        print('Updated value function:')
        for state in policyEvalStates:
            print(valNet.activate([state]))        
        
        # 4. Update policy based on current values 
        polNet = mb1.makeGreedy1D(valNet, polNet, policyEvalStates,numAct,stepSize)
        print('Updated policy:')
        for state in policyEvalStates:
            print(np.argmax(polNet.activate([state])))
    
def mainModelBased():
    # 1. Create a random value function
    dimState = 2 # Number of state variables (position from thermal, height)
    numHiddenVal = 20 # Number of hidden neurons
    valNet = createValNetwork(dimState,numHiddenVal)  # Using two hidden layers for precision  
    
    # 2. Create a random policy network
    numHiddenPol = 20 # Number of hidden neurons
    numAng = 2
    numAct = numAng + 1 # Number of actions (additional action is for orbit)
    polNet = createPolNetwork(dimState, numHiddenPol, numAct)       
    
    
    # 3. Update values based on current policy
    # The policy is greedy with respect to the value estimates
    
    # 3a. Determine subset of state to update on
    # It isn't practical to visit every possible state
    # Instead, we will work on a discretized version of the state space, and trust to the neural network for interpolation    
    # Here we set the states used to update the policy
    start = 0
    stop = 10    
    evalDist = np.linspace(start, stop, num=7)
    evalHeight = np.linspace(start, stop, num=1)
    
    import itertools
    policyEvalStates = list(itertools.product(evalDist,evalHeight)) # Takes cartesian product
    
    # Print initial policy
    print('Initial policy:')
    print('Choice \t State')
    for state in policyEvalStates:
        print(np.argmax(polNet.activate(state)), '\t', state)   
    
    # Make values consistent with policy
    import evalPolicy
    vMaxAll = 0.1 # We require values to stop changing by any more than this amount before we return the updated values
    stepSize = 0.1 # How far the airplane moves each time (needed to predict next state)
    thermRadius = 3 # Standard deviation of normal shaped thermal   
    
    numLearn = 100 # Number of times to repeat learning cycle
    
    for i in range(numLearn):   
        valNet = evalPolicy.evalPolicy(valNet,polNet,policyEvalStates,vMaxAll, stepSize, thermRadius)
        
        # Print new value network on selected points
        print('Updated value function:')
        print('Value \t State')
        for state in policyEvalStates:
            print(valNet.activate(state), '\t', state)        
        
        # 4. Update policy based on current values 
        import updatePolicy
        polNet = updatePolicy.makeGreedy(valNet, polNet, policyEvalStates,numAct,stepSize, thermRadius)
        print('Updated policy:')
        print('Choice \t State')
        for state in policyEvalStates:
            print(np.argmax(polNet.activate(state)), '\t', state)   

#mainModelBased1D() # Only keeps track of distance to thermal
mainModelBased()
