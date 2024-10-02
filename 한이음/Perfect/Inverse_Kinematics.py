import math

class DeltaRobot:
    class Move:
        def __init__(self):
            self.a = 100.0
            self.b = 260.0
            self.c = 600.0
            self.d = 42.5
            self.posX = 250
            self.posY = -250
            self.posZ = 502

        def deltakinematic(self, servo):
            pi120 = 120.0 * (math.pi / 180.0)
            pi240 = 240.0 * (math.pi / 180.0)
            pi180 = 180.0 * (math.pi / 180.0)
            pi300 = 300.0 * (math.pi / 180.0)
            pi420 = 420.0 * (math.pi / 180.0)

            x = y = z = 0.0
            
            if servo == 'A':
                x = math.cos(pi180) * self.posX + math.sin(pi180) * self.posY
                y = -math.sin(pi180) * self.posX + math.cos(pi180) * self.posY
                z = self.posZ

            if servo == 'B':
                x = math.cos(pi300) * self.posX + math.sin(pi300) * self.posY
                y = -math.sin(pi300) * self.posX + math.cos(pi300) * self.posY
                z = self.posZ

            if servo == 'C':
                x = math.cos(pi420) * self.posX + math.sin(pi420) * self.posY
                y = -math.sin(pi420) * self.posX + math.cos(pi420) * self.posY
                z = self.posZ

            length1 = (self.a - self.d - y)
            alpha = (360.0 / (2.0 * math.pi)) * math.atan2(z, length1)
            length2 = math.sqrt(math.pow(self.c, 2) - math.pow(x, 2))
            length3 = math.sqrt(math.pow(length1, 2) + math.pow(z, 2))

            cosine_angle = (math.pow(length3, 2) - math.pow(length2, 2) + math.pow(self.b, 2)) / (2.0 * length2 * self.b)
            beta = (360.0 / (2.0 * math.pi)) * math.acos(cosine_angle)
            gamma = 180.0 - alpha - beta

            return gamma

# 객체 생성 및 위치 설정
robot_move = DeltaRobot.Move()

minus=10.046

AA=robot_move.deltakinematic('A')-minus
BB=robot_move.deltakinematic('B')-minus
CC=robot_move.deltakinematic('C')-minus
print("AA:", AA)
print("BB:", BB)
print("CC:", CC)

print("Gamma for servo A:", robot_move.deltakinematic('A'))
print("Gamma for servo B:", robot_move.deltakinematic('B'))
print("Gamma for servo C:", robot_move.deltakinematic('C'))
