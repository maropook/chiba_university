def step_function(x):
    return np.array(x > 0, dtype=int)


def AND2(x):
    w = np.array([0.5, 0.5])
    b = -0.7
    tmp = np.dot(x, w) + b

    return step_function(tmp)


ANDを置き換える


def OR(x1, x2):
    x = np.array([x1, x2])
    w = np.array([1.0, 1.0])
    b = -0.5
    tmp = np.sum(w * x) + b
    if tmp <= 0:
        return 0
    else:
        return 1


def OR2(x):
    w = np.array([1.0, 1.0])
    b = -0.5
    tmp = np.dot(x, w) + b

    return step_function(tmp)


x_00 = np.array([0, 0])
x_01 = np.array([0, 1])
x_10 = np.array([1, 0])
x_11 = np.array([1, 1])
print(f"OR2(0,0): {OR2(x_00)}")
print(f"OR2(0,1): {OR2(x_01)}")
print(f"OR2(1,0): {OR2(x_10)}")
print(f"OR2(1,1): {OR2(x_11)}")
