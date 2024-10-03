#include <ax12.h>
#include <math.h>

#define ARRAY_SIZE(x) ((int)(sizeof(x) / sizeof((x)[0])))

const int MX28_SERVO_POS_CENTER = 2048;
const float MX28_TICKS_PER_DEGREE = 11.37778f;
const float MX28_DEGREES_PER_TICK = 0.08789f;
const int MX28_DEFAULT_SPEED = 40;

const int MX28_SERVO_IDS[] = {
	1,
	2
};

const int MX28_SERVO_POS_OFFSETS[] = {
	0,
	1024
};

const int MX28_SERVO_POS_RANGES[][2] = {
	{ 0,    4096 },
	{ 2048, 4096 }
};

bool AcceptCommand = false;
char SerialCmdBuffer[256] = { 0 };

void setup()
{
	// ArbotiX IO port for controlling Servos
	pinMode(0, OUTPUT);

	Serial.begin(19200);
	delay(500);
	CheckVoltage();
	AcceptCommand = true;
	Reset();
}

void loop()
{
	// Get commands  
	int numChars = Serial.readBytesUntil('\n', SerialCmdBuffer, ARRAY_SIZE(SerialCmdBuffer) - 1);
	if (!AcceptCommand || numChars == 0)
		return;

	SerialCmdBuffer[numChars] = '\0';

	switch (SerialCmdBuffer[0])
	{
	case '?': // Help   
	case 'h': // Help   
		Serial.print("Commands:\n");
		Serial.print("Reset:      r\n");
		Serial.print("Center:     c\n");
		Serial.print("Move:       m <id> <position +/- 180 degrees>\n");
		Serial.print("Speed:      s <id> <speed 0 - 1023>\n");
		Serial.print("Stop:       k <id>\n");
		Serial.print("Status:     q\n");

		CheckVoltage();
		break;

	case 'r':
		Reset();
		break;

	case 'm':
		MoveServo();
		break;

	case 'c':
		CenterAllServos();
		break;

	case 'g':
		ReadPosition();
		break;

	case 'k':
		StopServo();
		break;

	case 's':
		SetServoSpeed();
		break;

	case 'q':
		GetStatus();
		break;

	default:
		Serial.print("ERROR: Unknown Command from PC: ");
		Serial.print(SerialCmdBuffer);
		Serial.print("\n");
		break;
	}
}

int GetServoIndex(int id)
{
	for (int i = 0; i < ARRAY_SIZE(MX28_SERVO_IDS); i++)
	{
		if (MX28_SERVO_IDS[i] == id)
			return i;
	}

	return -1;
}

void ReadPosition()
{
	int servoID, servoIDX;

	if (sscanf(SerialCmdBuffer, "g %d", &servoID) != 1)
	{
		Serial.print("ERROR: Invalid command!\n");
		return;
	}

	servoIDX = GetServoIndex(servoID);
	if (servoIDX < 0)
	{
		Serial.print("ERROR: Invalid Servo ID!\n");
		return;
	}

	int positionTicks = GetPosition(MX28_SERVO_IDS[servoIDX]);
	float positionDegrees = (positionTicks - (MX28_SERVO_POS_CENTER + MX28_SERVO_POS_OFFSETS[servoIDX])) * MX28_DEGREES_PER_TICK;
	Serial.print(positionDegrees, 2);
	Serial.print("\n");
}

void MoveServo()
{
	int servoID, servoIDX;
	float positionDegrees;
	int i;
	int start;
	int wordIDX;
	int len;

	start = 0;
	wordIDX = 0;
	len = strlen(SerialCmdBuffer);
	for (i = 0; i <= len; i++)
	{
		if ((SerialCmdBuffer[i] == ' ')
			|| (SerialCmdBuffer[i] == '\0')
			)
		{
			SerialCmdBuffer[i] = '\0';

			switch (wordIDX)
			{
			case 0:
				if (SerialCmdBuffer[start] != 'm')
				{
					Serial.print("ERROR: Invalid command, 1st character should be m!\n");
					return;
				}
				break;

			case 1:
				servoID = atoi(&SerialCmdBuffer[start]);
				break;

			case 2:
				positionDegrees = atof(&SerialCmdBuffer[start]);
				break;

			default:
				break;
			}
			wordIDX++;
			start = i + 1;
		}
	}

	if (wordIDX != 3)
	{
		Serial.print("ERROR: Invalid command!\n");
		return;
	}


	servoIDX = GetServoIndex(servoID);
	if (servoIDX < 0)
	{
		Serial.print("ERROR: Invalid Servo ID!\n");
		return;
	}

	int positionTicks = MX28_SERVO_POS_CENTER + MX28_SERVO_POS_OFFSETS[servoIDX] + (int)(positionDegrees * MX28_TICKS_PER_DEGREE);
	SetPosition(MX28_SERVO_IDS[servoIDX], positionTicks);
	Serial.print("OK\n");
}

void SetServoSpeed()
{
	int servoID, servoIDX;
	int speed;

	if (sscanf(SerialCmdBuffer, "s %d %d", &servoID, &speed) != 2)
	{
		Serial.print("ERROR: Invalid command!\n");
		return;
	}

	servoIDX = GetServoIndex(servoID);
	if (servoIDX < 0)
	{
		Serial.print("ERROR: Invalid Servo ID!\n");
		return;
	}

	ax12SetRegister2(servoIDX, AX_GOAL_SPEED_L, speed); // Sets 2 bytes at a time (low and high byte)
	Serial.print("OK\n");
}

void CenterAllServos()
{
	for (int i = 0; i < ARRAY_SIZE(MX28_SERVO_IDS); i++)
		SetPosition(MX28_SERVO_IDS[i], MX28_SERVO_POS_CENTER + MX28_SERVO_POS_OFFSETS[i]);

	Serial.print("OK\n");
}

void StopServo()
{
	int servoID, servoIDX;

	if (sscanf(SerialCmdBuffer, "k %d", &servoID) != 1)
	{
		Serial.print("ERROR: Invalid command!\n");
		return;
	}

	servoIDX = GetServoIndex(servoID);
	if (servoIDX < 0)
	{
		Serial.print("ERROR: Invalid Servo ID!\n");
		return;
	}

	SetPosition(MX28_SERVO_IDS[servoIDX], GetPosition(MX28_SERVO_IDS[servoIDX]));
	Serial.print("OK\n");
}

void GetStatus()
{
	bool moving = false;

	for (int i = 0; i < ARRAY_SIZE(MX28_SERVO_IDS); i++)
	{
		if (ax12GetRegister(MX28_SERVO_IDS[i], AX_MOVING, 2) != 0)
		{
			moving = true;
			break;
		}
	}

	if (moving)
		Serial.print("MOVING\n");
	else
		Serial.print("IDLE\n");
}

void Reset()
{
	for (int i = 0; i < ARRAY_SIZE(MX28_SERVO_IDS); i++)
	{
		ax12SetRegister2(MX28_SERVO_IDS[i], AX_GOAL_SPEED_L, MX28_DEFAULT_SPEED);
		int positionTicks = MX28_SERVO_POS_CENTER + MX28_SERVO_POS_OFFSETS[i];
		SetPosition(MX28_SERVO_IDS[i], positionTicks);
	}
	Serial.print("READY\n");
}

void CheckVoltage()
{
	// wait, then check the voltage (LiPO safety)
	float voltage = (ax12GetRegister(1, AX_PRESENT_VOLTAGE, 1)) / 10.0f;
	Serial.print("System Voltage (as measured by servo): ");
	Serial.print(voltage, 2);
	Serial.print(" V\n");
	if (voltage < 10.0f)
	{
		Serial.print("Voltage levels below 10 V, please charge battery!\n");
		die();
	}
	else
		Serial.print("Voltage levels nominal.\n");
}

void die()
{
	while (1)
	{
	}
}

