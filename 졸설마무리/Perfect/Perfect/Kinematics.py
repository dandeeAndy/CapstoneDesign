import math

# 로봇 기하학 상수
e = 138.56  # 엔드 이펙터 크기
f = 346.41  # 베이스 크기
re = 600.0  # 엔드 이펙터와 조인트 사이의 거리
rf = 260.0  # 베이스와 조인트 사이의 거리

# 삼각 함수 상수
sqrt3 = math.sqrt(3.0)
pi = 3.141592653  # PI
sin120 = sqrt3 / 2.0
cos120 = -0.5
tan60 = sqrt3
sin30 = 0.5
tan30 = 1 / sqrt3

# 순운동학 계산 함수: (theta1, theta2, theta3) -> (x0, y0, z0)
# 반환된 상태: 0=정상, -1=존재하지 않는 위치
def delta_calcForward(theta1, theta2, theta3):
    t = (f - e) * tan30 / 2
    dtr = pi / 180.0  # Degree to Radian 변환을 위한 상수

    theta1 *= dtr
    theta2 *= dtr
    theta3 *= dtr

    y1 = -(t + rf * math.cos(theta1))
    z1 = -rf * math.sin(theta1)

    y2 = (t + rf * math.cos(theta2)) * sin30
    x2 = y2 * tan60
    z2 = -rf * math.sin(theta2)

    y3 = (t + rf * math.cos(theta3)) * sin30
    x3 = -y3 * tan60
    z3 = -rf * math.sin(theta3)

    dnm = (y2 - y1) * x3 - (y3 - y1) * x2

    w1 = y1 * y1 + z1 * z1
    w2 = x2 * x2 + y2 * y2 + z2 * z2
    w3 = x3 * x3 + y3 * y3 + z3 * z3
    
    # x = (a1*z + b1)/dnm
    a1 = (z2 - z1) * (y3 - y1) - (z3 - z1) * (y2 - y1)
    b1 = -((w2 - w1) * (y3 - y1) - (w3 - w1) * (y2 - y1)) / 2.0

    # y = (a2*z + b2)/dnm
    a2 = -(z2 - z1) * x3 + (z3 - z1) * x2
    b2 = ((w2 - w1) * x3 - (w3 - w1) * x2) / 2.0

    # a*z^2 + b*z + c = 0
    a = a1 * a1 + a2 * a2 + dnm * dnm
    b = 2 * (a1 * b1 + a2 * (b2 - y1 * dnm) - z1 * dnm * dnm)
    c = (b2 - y1 * dnm) * (b2 - y1 * dnm) + b1 * b1 + dnm * dnm * (z1 * z1 - re * re)

    # 판별식
    d = b * b - 4.0 * a * c
    if d < 0:
        return -1, None, None, None  # 존재하지 않는 지점

    z0 = -0.5 * (b + math.sqrt(d)) / a
    x0 = (a1 * z0 + b1) / dnm
    y0 = (a2 * z0 + b2) / dnm
    return 0, x0, y0, z0

# 세타 값 모두 0으로 설정하여 함수 호출
theta1 = 31
theta2 = -39
theta3 = -20

result, x0, y0, z0 = delta_calcForward(theta1, theta2, theta3)
if result == 0:
    print(f"결과: x0 = {-x0}, y0 = {-y0}, z0 = {-z0}")
else:
    print("존재하지 않는 지점입니다.")
