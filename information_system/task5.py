import numpy as np


def step_function(x):
    return np.array(x > 0, dtype=int)


def init_network():
    # 第1層: NAND と OR を並列に計算
    #   列0 (NAND): w=[-0.5, -0.5], b= 0.7
    #   列1 (OR)  : w=[ 0.5,  0.5], b=-0.3
    # 第2層: AND を計算
    #   w=[0.5, 0.5], b=-0.7
    # XOR = AND( NAND(x1,x2), OR(x1,x2) )
    network = {}
    network['W1'] = np.array([[-0.5,  0.5],
                               [-0.5,  0.5]])
    network['b1'] = np.array([0.7, -0.3])
    network['W2'] = np.array([[0.5],
                               [0.5]])
    network['b2'] = np.array([-0.7])
    return network


def forward(network, x):
    W1, W2 = network['W1'], network['W2']
    b1, b2 = network['b1'], network['b2']

    a1 = np.dot(x, W1) + b1
    z1 = step_function(a1)   # [NAND(x), OR(x)]

    a2 = np.dot(z1, W2) + b2
    y = step_function(a2)    # XOR(x)

    return int(y[0])


network = init_network()

print("x1  x2  XOR")
print("-----------")
for x1, x2 in [(0, 0), (0, 1), (1, 0), (1, 1)]:
    x = np.array([x1, x2])
    y = forward(network, x)
    print(f" {x1}   {x2}   {y}")
