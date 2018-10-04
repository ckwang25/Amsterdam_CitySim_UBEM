import numpy as np

def definePinputs(yearRang, gridSize, idx):
    error1 = 0.3
    error2 = 0.15
    if yearRang == "1964":
        p_Uroof = np.linspace(0.17, 2.41 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 2.66 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 3.14 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.5 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "65_74":
        p_Uroof = np.linspace(0.17, 1.16 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 2.33 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 2.88 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.4 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "75_91":
        p_Uroof = np.linspace(0.17, 0.68 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.68 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 1.15 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 3.13 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "92_05":
        p_Uroof = np.linspace(0.17, 0.4 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.4 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.4 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 2.08 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    elif yearRang == "06_14":
        p_Uroof = np.linspace(0.17, 0.25 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.29 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.29 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 1.85 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    else:
        p_Uroof = np.linspace(0.17, 0.17 + error1, gridSize)
        p_Uwall = np.linspace(0.22, 0.22 + error1, gridSize)
        p_Ufloor = np.linspace(0.29, 0.29 + error1, gridSize)
        p_Uwindow = np.linspace(1.8, 1.8 + error2, gridSize)
        consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]

    p_Uroof = consturctionData[0][idx]
    p_Uwall = consturctionData[1][idx]
    p_Ufloor = consturctionData[2][idx]
    p_Uwindow = consturctionData[3][idx]

    return p_Uroof, p_Uwall, p_Ufloor, p_Uwindow

gridSize = 5
print definePinputs('2015', gridSize, 4)

def defineInputs(yearRang):
    # consturctionData = [p_Uroof, p_Uwall, p_Ufloor, p_Uwindow]
    if yearRang == "1964":
        consturctionData = [2.41, 2.66, 3.14, 3.5]
    elif yearRang == "65_74":
        consturctionData = [1.16, 2.33, 2.88, 3.4]
    elif yearRang == "75_91":
        consturctionData = [0.68, 0.68, 1.15, 3.13]
    elif yearRang == "92_05":
        consturctionData = [0.4, 0.4, 0.4, 2.08]
    elif yearRang == "06_14":
        consturctionData = [0.25, 0.29, 0.29, 1.85]
    else:
        consturctionData = [0.17, 0.22, 0.29, 1.8]

    p_Uroof = consturctionData[0]
    p_Uwall = consturctionData[1]
    p_Ufloor = consturctionData[2]
    p_Uwindow = consturctionData[3]

    return p_Uroof, p_Uwall, p_Ufloor, p_Uwindow