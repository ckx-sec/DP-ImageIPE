import random
import numpy as np
import math
import csv


class ImageFeatureIPE:
    def __init__(self, len, p, g):
        self.g = g
        self.p = p
        self.msk = s = [random.random() for _ in range(len)]
        self.mpk = h = [pow(g, si) for si in s]

    def setup(self):
        return self.mpk, self.msk

    def encrypt(self, w):
        ct0 = []
        ctx = []
        for i in range(18):
            r = random.random()
            ct0.append(pow(self.g, r))
            ctx.append([pow(self.mpk[j], r)*pow(self.g, w[i][j])
                        for j in range(512)])
        return ct0, ctx

    def keyGenerate(self, z):
        s = np.array(self.msk)
        z = np.array(z)
        sk = list(np.matmul(s, z))
        return sk

    def padding(z, r=7, n=0):
        for i in range(1, n+1):
            z[-i] = [(random.random()-0.5)*r for _ in range(512)]
        return z

    def decrypt(self, ctx, ct0, sk, mpks):
        a = []
        val = 1
        for i in range(18):
            b = []
            for j in range(512):
                fenzi = 1
                fenmu = 1
                val = 1
                for k in range(512):
                    fenzi *= pow(ctx[i][k], mpks[j][k])
                fenmu = pow(ct0[i], sk[i])
                #val *= fenzi/fenmu
                # print(val)
                b.append(fenzi/fenmu)
            a.append(b)
        return a


def noisyCount(sensitivety, epsilon):
    beta = sensitivety/epsilon
    u1 = np.random.random()
    u2 = np.random.random()
    if u1 <= 0.5:
        n_value = -beta*np.log(1.-u2)
    else:
        n_value = beta*np.log(u2)
    # print(n_value)
    return n_value


def laplace_mech(data, sensitivety, epsilon):
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] += noisyCount(sensitivety, epsilon)
    return data


if __name__ == "__main__":
    app = ImageFeatureIPE(512, p=0b010, g=1.0001)
    w = []
    for i in range(18):
        f = csv.reader(open('feature0.csv'))
        for row in f:
            w.append(list(map(lambda x: float(x), row)))
        #w.append([j for j in range(512)])
    mpks = [app.mpk]
    for _ in range(511):
        msk = s = [random.random() for _ in range(512)]
        mpk = h = [pow(app.g, si) for si in s]
        mpks.append(mpk)

    a = []
    for i in range(18):
        b = []
        for j in range(512):
            sum = 0
            for k in range(512):
                sum += w[i][k]*mpks[j][k]
            b.append(pow(app.g, sum))
        a.append(b)
    # print(a)
    open('data.txt', 'w').write(str(a))

    sensitivety = 1
    epsilon = 1
    w = laplace_mech(w, sensitivety, epsilon)

    ct0, ctx = app.encrypt(w)

    a = []
    for i in range(18):
        b = []
        for j in range(512):
            sum = 0
            for k in range(512):
                sum += w[i][k]*mpks[j][k]
            b.append(pow(app.g, sum))
        a.append(b)
    # print(a)
    open('modify.txt', 'w').write(str(a))

    sk = app.keyGenerate(mpks)
    de = app.decrypt(ctx, ct0, sk, mpks)
    open('de.txt', 'w').write(str(de))
