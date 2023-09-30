from time import sleep
import RPi.GPIO as GPIO


class SG90:
    def __init__(self, servo_pin):
        self.servo_pin = servo_pin

        # GPIO.setwarnings(False)
        # GPIO.setmode(self.gpio_mode)
        GPIO.setup(servo_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(servo_pin, 50)  # 50Hz
        self.pwm.start(7.5)  # 1.5ms

    def set_angle(self, angle):
        print("angle : ", angle)
        if 0 <= angle <= 180:
            duty_cycle = 2.5 + angle / 18  # デューティサイクルを計算
            self.pwm.ChangeDutyCycle(duty_cycle)  # デューティサイクルを設定
        else:
            print("Invalid angle. Enter an angle between 0 and 180 degrees.")

    def end(self):
        self.pwm.stop()
