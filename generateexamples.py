import math
import random
import json
import os

des = (5, 4.5, 8, 2)
inter = (50, 4.5, 0, 4)
none = (0, 0, 0, 0)
tur = (75, 2.5, 4, 0)
boosttur = (75, 2.5, 8, 0)
wall = (60, 0, 0, 0)
boostwall = (120, 0, 0, 0)
scorer = (17, 3, 2, 1)

def getfromtxt(text):
    des = (5, 4.5, 8, 2)
    inter = (50, 4.5, 0, 4)
    none = (0, 0, 0, 0)
    tur = (75, 2.5, 4, 0)
    boosttur = (75, 2.5, 8, 0)
    wall = (60, 0, 0, 0)
    boostwall = (120, 0, 0, 0)
    ret = []
    for txt in text.split(','):
        if (txt in ['des', 'inter', 'none', 'tur', 'boosttur', 'wall', 'boostwall', 'scorer']):
          ret.append([des, inter, none, tur, boosttur, wall, boostwall, scorer][['des', 'inter', 'none', 'tur', 'boosttur', 'wall', 'boostwall', 'scorer'].index(txt)])
    return ret
    
def tupstotxt(tups):
    des = (5, 4.5, 8, 2)
    inter = (50, 4.5, 0, 4)
    none = (0, 0, 0, 0)
    tur = (75, 2.5, 4, 0)
    boosttur = (75, 2.5, 8, 0)
    wall = (60, 0, 0, 0)
    boostwall = (120, 0, 0, 0)
    joiner = []
    for tup in tups:
        if (tup in [des, inter, none, tur, boosttur, wall, boostwall, scorer]):
            joiner.append(['des', 'inter', 'none', 'tur', 'boosttur', 'wall', 'boostwall', 'scorer'][[des, inter, none, tur, boosttur, wall, boostwall, scorer].index(tup)])
    return ','.join(joiner)

def healthstotxt(healths):
  return ",".join(list(map(str, list(healths))))

def txttohealths(txt):
  return list(map(int, txt.split(',')))

def gettrainingexample():
  types = []
  healths = []
  totalMP = 0
  for _ in range(9):
    typer = random.choice([none, tur, boosttur, boostwall, wall])
    types.append(typer)
    if typer != none:
      support = False
      if random.random() > 0.8:
        support = True
      if random.choice([0, 1]) == 0:
        healths.append(typer[0] + ((3 + round(5*random.random())) if support else 0))
      else:
        healths.append(round(typer[0] * random.random()) + (3 + round(5*random.random()) if support else 0))
    else:
      healths.append(0)
  if random.choice([0, 1]) == 0:
    totalMP = 15
  else:
    totalMP = 3 + round(12*random.random())

  return [types, healths, totalMP, findoptimal(types, healths, totalMP)]

def getdata():
  types = []
  healths = []
  for _ in range(9):
    typer = random.choice([none, tur, boosttur, boostwall, wall])
    types.append(typer)
    if typer != none:
      support = False
      if random.random() > 0.8:
        support = True
      if random.choice([0, 1]) == 0:
        healths.append(typer[0] + ((3 + round(5*random.random())) if support else 0))
      else:
        healths.append(round(typer[0] * random.random()) + (3 + round(5*random.random()) if support else 0))
    else:
      healths.append(0)

  return [types, healths]

def findoptimal(types, healths, totalMP):
  maxdest = min(totalMP // 3, 4)
  scored = -10
  MPused = 1000
  distribution = []
  for i in range(maxdest+1):
    for j in range(totalMP - 3*i):
      for k in range(2):
        scored1, MPused1, distribution1 = test(i, j, 2*k, types, healths, totalMP - 3*i - j)
        if scored1 > scored:
          scored = scored1
          MPused = MPused1
          distribution = distribution1
        elif scored1 == scored:
          if MPused1 < MPused:
            scored = scored1
            MPused = MPused1
            distribution = distribution1
  return [scored, MPused, distribution]


def test(i, j, k, types, healths, additional, wantremains=False):
  scorerpositions = [[11, 2], [12, 2], [12, 1], [13, 1], [14, 1], [15, 1], [15,2], [16, 2], [16, 3], [17, 3], [17, 4], [18, 4], [18, 5], [19, 5], [19, 6], [20, 6], [20, 7], [21, 7], [21, 8], [22, 8], [22, 9], [23, 9], [23, 10], [24, 10], [24, 11], [25, 11], [25, 12], [26, 12], [26, 13], [26, 14], [27, 14]]
  positions = [[19, 5], [19, 6], [20, 6], [20, 7], [21, 7], [21, 8], [22, 8], [22, 9], [23, 9], [23, 10], [24, 10], [24, 11], [25, 11], [25, 12], [26, 12], [26, 13], [26, 14], [27, 14]]
  attackerpositions = [[23, 14], [24, 14], [25, 14], [26, 14], [27, 14], [24, 15], [25, 15], [26, 15], [25, 16]]
  destroyer = [k, des[0]*i]
  biggies = [8, inter[0]*j]
  scorers = [0, scorer[0]*additional]
  attackers = []
  scored = 0
  # (location, type, health)
  for n in range(len(types)):
    attackers.append([n, types[n], healths[n]])

  for n in range(35):
    if (biggies[1] > 0):
      if (n % 4 == 3):
        if (biggies[0] == 15 and attackers[3][2] > 0) or (biggies[0] == 16 and attackers[4][2] > 0):
          for m in attackers:
            dist = distance(attackerpositions[m[0]], positions[biggies[0]])
            if dist <= 1.5:
              m[2] -= (biggies[1] // inter[0]) * inter[0]
          biggies[1] = 0
        elif (biggies[0] == 17):
          scored += (biggies[1] // inter[0])
          biggies[1] = 0
        else:
          biggies[0] += 1
          
    if (destroyer[1] > 0):
      if (n % 2 == 1):
        if (destroyer[0] == 15 and attackers[3][2] > 0) or (destroyer[0] == 16 and attackers[4][2] > 0):
          for m in attackers:
            dist = distance(attackerpositions[m[0]], positions[destroyer[0]])
            if dist <= 1.5:
              m[2] -= (destroyer[1] // des[0]) * des[0]
            destroyer[1] = 0
        elif (destroyer[0] == 17):
          scored += (destroyer[1] // des[0])
          destroyer[1] = 0
        else:
          destroyer[0] += 1

    if (scorers[1] > 0):
      if (scorers[0] == len(scorerpositions)-3 and attackers[3][2] > 0) or (scorers[0] == len(scorerpositions)-2 and attackers[4][2] > 0):
        for m in attackers:
            dist = distance(attackerpositions[m[0]], scorerpositions[scorers[0]])
            if dist <= 1.5:
              m[2] -= (scorers[1] // scorer[0]) * scorer[0]
        scorers[1] = 0
      elif (scorers[0] == len(scorerpositions)-1):
            scored += (scorers[1] // scorer[0])
            scorers[1] = 0
      else:
            scorers[0] += 1

    mindest = [1000, -1]
    minsc = [1000, -1]
    for x, m in enumerate(attackers):
      if (m[2] > 0):
        scdistance = distance(attackerpositions[m[0]], scorerpositions[scorers[0]])
        scdis = 10 if scdistance > 2.5 else scdistance
        if scdistance < minsc[0]:
          minsc = [scdistance, x]
        elif scdistance == minsc[0]:
          if m[2] < attackers[minsc[1]][2]:
            minsc = [scdistance, x]
          elif m[2] == attackers[minsc[1]][2]:
            if (attackerpositions[m[0]][1] < attackerpositions[attackers[minsc[1]][0]][1]):
              minsc = [scdistance, x]
            elif (attackerpositions[m[0]][1] == attackerpositions[attackers[minsc[1]][0]][1]):
              if (attackerpositions[m[0]][0] < attackerpositions[attackers[minsc[1]][0]][0]):
                minsc = [scdistance, x]
        destdistance = distance(attackerpositions[m[0]], positions[destroyer[0]])
        desdis = 10 if destdistance > 2.5 else destdistance
        if destdistance < mindest[0]:
          mindest = [destdistance, x]
        elif destdistance == mindest[0]:
          if m[2] < attackers[mindest[1]][2]:
            mindest = [destdistance, x]
          elif m[2] == attackers[mindest[1]][2]:
            if (attackerpositions[m[0]][1] < attackerpositions[attackers[mindest[1]][0]][1]):
              mindest = [destdistance, x]
            elif (attackerpositions[m[0]][1] == attackerpositions[attackers[mindest[1]][0]][1]):
              if (attackerpositions[m[0]][0] < attackerpositions[attackers[mindest[1]][0]][0]):
                mindest = [destdistance, x]
        bigdistance = distance(attackerpositions[m[0]], positions[biggies[0]])
        bigdis = 10 if bigdistance > 2.5 else bigdistance
        if (m[2] > 0):
          a = min(desdis, bigdis, scdis)
          if a < 10:
            if a == bigdis:
              biggies[1] -= m[1][2]
            elif a == desdis:
              destroyer[1] -= m[1][2]
            else:
              scorers[1] -=m[1][2]
              
    if (destroyer[1] > 0 and mindest[0] < des[1]):
      attackers[mindest[1]][2] -= (destroyer[1] // des[0]) * des[2]

    if (scorers[1] > 0 and minsc[0] < scorer[1]):
      attackers[minsc[1]][2] -= (scorers[1] // scorer[0]) * scorer[2]

  if wantremains:
    remaining = 0
    for m in attackers:
      remaining += max(m[2], 0)
    return (scored, 3*i+j, [i, j, k], remaining)
  return (scored, 3*i+j, [i, j, k])
  
def distance(pos1, pos2):
  return round(10 * math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)) / 10

if __name__ == "__main__":
    os.chdir('./examples')
    for i in range(100):
        storage = {}
        try: 
          f = open(f"example{i}.json", "w")
        except:
          f = open(f"example{i}.json", "x")
        f.close()
        for j in range(100):
            example = gettrainingexample()
            storage["$".join([tupstotxt(example[0]), healthstotxt(example[1]), str(example[2])])] = example[3]
        print(f"example {i} done")
        json_object = json.dumps(storage)
        with open(f"example{i}.json", "w") as outfile:
            outfile.write(json_object)