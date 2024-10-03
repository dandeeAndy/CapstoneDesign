import math

class DeltaRobot:
    class Move:
        def __init__(self, length_a, length_b, length_c, length_d):
            self.length = {
                'a': length_a,
                'b': length_b,
                'c': length_c,
                'd': length_d
            }

        def deltakinematic(self, posX, posY, posZ, servo):
            x = 0.0
            y = 0.0
            z = 0.0
            pi120 = 120.0 * (math.pi / 180.0)
            pi240 = 240.0 * (math.pi / 180.0)

            if servo == 'A':
                x = posX
                y = posY
                z = posZ

            if servo == 'B':
                x = (math.cos(pi120) * posX) + (math.sin(pi120) * posY)
                y = -(math.sin(pi120) * posX) + (math.cos(pi120) * posY)
                z = posZ

            if servo == 'C':
                x = (math.cos(pi240) * posX) + (math.sin(pi240) * posY)
                y = -(math.sin(pi240) * posX) + (math.cos(pi240) * posY)
                z = posZ

            length1 = self.length['a'] - self.length['d'] - y
            alpha = (360.0 / (2.0 * math.pi)) * math.atan2(z, length1)

            length2 = math.sqrt(math.pow(length1, 2.0) + math.pow(z, 2.0))
            length3 = math.sqrt(math.pow(self.length['c'], 2.0) - math.pow(x, 2.0))

            beta = (360.0 / (2.0 * math.pi)) * math.acos((math.pow(length3, 2) - math.pow(length2, 2.0) - math.pow(self.length['b'], 2.0)) / (-2.0 * length2 * self.length['b']))

            gamma = 180.0 - alpha - beta

            return gamma
    
robot_move = DeltaRobot.Move()

print("Gamma for servo A:", robot_move.deltakinematic('A'))
print("Gamma for servo B:", robot_move.deltakinematic('B'))
print("Gamma for servo C:", robot_move.deltakinematic('C'))