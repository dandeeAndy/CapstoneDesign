import  math

class IK:
    class Move:
        def __init__(self):
            self.a = 100.0
            self.b = 260.0
            self.c = 600.0
            self.d = 42.5
            
        def set_position(self, x, y, z):
            self.posX, self.posY, self.posZ = x, y, z
            
        def deltakinematic(self, servo):
            pi180 = 180.0 * (math.pi / 180.0)
            pi300 = 300.0 * (math.pi / 180.0)
            pi420 = 420.0 * (math.pi / 180.0)

            x = y = z = 0.0
            
            if servo == 'A':
                x = math.cos(pi180) * self.posX + math.sin(pi180) * self.posY
                y = -math.sin(pi180) * self.posX + math.cos(pi180) * self.posY
                z = self.posZ
            elif servo == 'B':
                x = math.cos(pi300) * self.posX + math.sin(pi300) * self.posY
                y = -math.sin(pi300) * self.posX + math.cos(pi300) * self.posY
                z = self.posZ
            elif servo == 'C':
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

    @staticmethod
    def c_deg(x, y, z):
        robot_move = IK.Move()
        robot_move.set_position(x, y, z)
        minus = 10.046
        # degree_motor1 = round(robot_move.deltakinematic('A'), 3) - minus
        # degree_motor2 = round(robot_move.deltakinematic('B'), 3) - minus
        # degree_motor3 = round(robot_move.deltakinematic('C'), 3) - minus
        degree_motor1 = robot_move.deltakinematic('A') - minus
        degree_motor2 = robot_move.deltakinematic('B') - minus
        degree_motor3 = robot_move.deltakinematic('C') - minus
        return [degree_motor1, degree_motor2, degree_motor3]
    
