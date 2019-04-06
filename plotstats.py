import os
import matplotlib.pyplot as plt

def select(running, fixed, value):
    selected = []
    for stat in stats:
        if getattr(stat,fixed) == value:
            selected.append((getattr(stat,running),stat.Tg,stat.Tn))
    selected.sort()
    x = [a for a,b,c in selected]
    Tg = [b for a,b,c in selected]
    Tn = [c for a,b,c in selected]
    return x, Tg, Tn

def select2(running, fixed, value, fixed2, value2):
    selected = []
    for stat in stats:
        if getattr(stat,fixed) == value and getattr(stat,fixed2) == value2:
            selected.append((getattr(stat,running),stat.Tg,stat.Tn))
    selected.sort()
    x = [a for a,b,c in selected]
    Tg = [b for a,b,c in selected]
    Tn = [c for a,b,c in selected]
    return x, Tg, Tn

class Stat:
    def __init__(self, N, R, F, Tg, Tn):
        self.N = N
        self.R = R
        self.F = F
        self.Tg = Tg
        self.Tn = Tn


stats = []
with open("stats.dat","r") as f:
    for line in f.readlines():
        N,R,F,Tg,Tn = [float(x) for x in line.replace("\n","").split(" ")]
        stats.append(Stat(N,R,F,Tg,Tn))


NS = sorted(list(set([x.N for x in stats])))
RS = sorted(list(set([x.R for x in stats])))
FS = sorted(list(set([x.F for x in stats])))

print("N's =",NS)
print("R's =",RS)
print("F's =",FS)

# N's = [2.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0]
# R's = [2.0, 5.0, 10.0]
# F's = [2.0, 3.0, 5.0, 10.0]

plt.clf()
plt.grid()

# F = 2
# R = 5
# N, Tg, Tn = select2("N","F",F,"R",R)
# plt.plot(N, Tg, "o-", label="Grid (R,F)="+str(R)+","+str(F))
# plt.plot(N, Tn, "x-", label="Naive (R,F)="+str(R)+","+str(F))
#
# F = 10
# R = 5
# N, Tg, Tn = select2("N","F",F,"R",R)
# plt.plot(N, Tg, "o-", label="Grid (R,F)="+str(R)+","+str(F))
# plt.plot(N, Tn, "x-", label="Naive (R,F)="+str(R)+","+str(F))

colors = ["r","y","b","k","g"]
symbols = ["o","x","s"]
i = 0
for F in FS:
    for R in RS:
        i += 1
        color = colors[i%len(colors)]
        symb = symbols[i%len(symbols)]
        N, Tg, Tn = select2("N","F",F,"R",R)
        plt.plot(N, Tg, color+symb+"-", label="Grid (R,F)="+str(int(R))+","+str(int(F)))
plt.plot(N, Tn, "--", label="Naive")


plt.legend(loc="upper left")
plt.xlabel("Number of particles")
plt.ylabel("Computation time")
plt.show()
