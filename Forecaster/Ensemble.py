import pandas as pd
import os
import math
os.environ['KMP_DUPLICATE_LIB_OK']='True'
def loadData(choice):
    f_csv = 'Data/ResultCSV-' + str(choice) + '.csv'
    print(f_csv)
    data = pd.read_csv(f_csv)
    #LSTM,GAN,TCN,FNN,LR,True
    data = data.values
    X = data[:,1:6] #(1194，5)
    Y = data[:,6] #(1194,)
    return X,Y

def calculate_sm(Y,X,gam):#x truth,y predict
    ans = 0.0
    sumgamma = 0.0
    for i in range(len(X)-10,len(X)):
        y = Y[i]
        x = X[i]
        gamma = math.pow(gam, len(X)-i)
        #mape = abs((x*205+304)-(y*205+304))/abs(x*205+304)
        mse = (y - x) ** 2
        #print(mse)
        #print(gamma)
        sm = mse * gamma
        ans = ans + sm
    #print(ans)
    #ans = ans/(len(X)+1)
    #print(ans)
    return ans

def calculate_mse(X,Y):
    mse =sum([(y - x) ** 2 for x, y in zip(X, Y)]) / len(X)
    print('The MSE is ', mse)
    return mse

for i in range(0,5):
    X, Y = loadData(i)
    TCN = list()
    FNN = list()
    GAN = list()
    #print("LSTM")
    #calculate_mse(X[:, 0],Y)
    print("TCN")
    calculate_mse(X[:, 1], Y)
    print("GAN")
    calculate_mse(X[:, 2], Y)
    print("FNN")
    calculate_mse(X[:, 3], Y)
    #print("LR")
    #calculate_mse(X[:, 4], Y)
    TCN = X[:, 1]
    FNN = X[:, 3]
    GAN = X[:, 2]
    Esm = list()
    for j in range(10):
        Esm.append(TCN[j]/3+FNN[j]/3+GAN[j]/3)
    #print(Esm)
    for j in range(10,len(TCN)-1):
        st = calculate_sm(TCN[:j], Y[:j],0.9)
        sf = calculate_sm(FNN[:j], Y[:j],0.9)
        sg = calculate_sm(GAN[:j], Y[:j],0.9)
        #wt = st / (st + sf + sg)
        #wf = sf / (st + sf + sg)
        #wg = sg / (st + sf + sg)
        wt = 0.5 * (sf+sg) / (st + sf + sg)
        wf = 0.5 * (st+sg)/ (st + sf + sg)
        wg = 0.5 * (st+sf) / (st + sf + sg)
        
        #print(wt,wf,wg)
        xe = TCN[j+1]*wt + FNN[j+1]*wf + GAN[j+1]*wg
        Esm.append(xe)
    print("Ensemle")
    calculate_mse(Esm, Y)
    #print(Esm)
    print("/3")
    calculate_mse(X[:, 1]/3+X[:, 2]/3+X[:, 3]/3, Y)
    #print(X[:, 1]/3+X[:, 2]/3+X[:, 3]/3)

