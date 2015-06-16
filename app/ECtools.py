# -*- coding: utf-8 -*-

# ==== Dictionary Loader (utf-8) ====
def loadDict (dictPath):
    loadList = []
    with open(dictPath, 'r') as rfile:
        rdata = rfile.read().splitlines()
        for term in rdata:
            loadList += [term.decode('utf-8')]

    return loadList

# ==== Prediction by matching the subsequence ====
def preDict (query, sadDict, sorryDict, angryDict, happyDict, weight):
    emoList = [0.0, 0.0, 0.0, 0.0]
    for term in sadDict:
        if term in query:
            emoList[0] += weight * len(term)
    for term in sorryDict:
        if term in query:
            emoList[1] += weight * len(term)
    for term in angryDict:
        if term in query:
            emoList[2] += weight * len(term)
    for term in happyDict:
        if term in query:
            emoList[3] += weight * len(term)
    return emoList

# ==== Calculate the Label of the input emoList ====
def labelMe (emoList, R):
    topLabelValue = max(emoList)
    tList = emoList[:]    # find second position label by del the top label
    del tList[emoList.index(topLabelValue)]
    secondLabelValue = max(tList)
    if secondLabelValue > topLabelValue * (1 - R):
        return 0
    else:
        return emoList.index(topLabelValue) + 1

# ==== transfer 4-d to 5-d (plus [none] value) ====
def finalVec (emoList, R):
    topLabelValue = max(emoList)
    tList = emoList[:]    # find second position label by del the top label
    del tList[emoList.index(topLabelValue)]
    secondLabelValue = max(tList)
    if secondLabelValue >= topLabelValue * (1 - R):
        none = 2.0 * (R - ((topLabelValue - secondLabelValue) / (topLabelValue + 0.000001))) / R
        emoList = [float(none)] + emoList

        emoSum = 0.000001    #    avoiding dividing zero
        for i in range(5):
            emoSum += emoList[i]
        for i in range(5):
            emoList[i] /= emoSum
        return emoList
    else:
        return [0] + emoList

# ==== Parameter adjusting PHASE ====
def adjuster (para = [0.3, 0.2, 0.2, 0.3, 0.15, 0.15, 0.35, 0.35], S = 0.1, label = [0, 0, 0, 0, 0, 0], FL = 0):
    C = para[0]
    SC = para[1]
    CX = para[2]
    N = para[3]
    D = para[4]
    P = para[5]
    I = para[6]
    A = para[7]

    CL = label[0]
    SCL = label[1]
    CXL = label[2]
    NL = label[3]
    IL = label[4]
    AL = label[5]

    if FL != CL:
        C *= (1 - S)
    if FL != SCL:
        SC *= (1 - S)
    if FL != CXL:
        CX *= (1 - S)
    if FL != NL:
        N *= (1 - S)

    dSum = C + SC + CX + N
    C /= dSum
    SC /= dSum
    CX /= dSum
    N /= dSum

    if FL != IL:
        I *= (1 - S)
    if FL != AL:
        A *= (1 - S)
    oSum = D + I + A
    D /= oSum * (1 - P)
    I /= oSum * (1 - P)
    A /= oSum * (1 - P)

    return [C, SC, CX, N, D, P, I, A]