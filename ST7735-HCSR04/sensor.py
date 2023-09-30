import time
import math
import RPi.GPIO as GPIO


class HCSR04:
    def __init__(self, trig_pin, echo_pin, temperature=20):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.speed_of_sound = 331.3 * math.sqrt(1 + (temperature / 273.15))

        # GPIO.setwarnings(False)
        # GPIO.setmode(self.gpio_mode)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def get_distance(self):
        """Return an unformatted distance in cm's as read directly from RPi.GPIO."""
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trig_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)
        echo_status_counter = 1
        while GPIO.input(self.echo_pin) == 0:
            if echo_status_counter < 1000:
                sonar_signal_off = time.time()
                echo_status_counter += 1
            else:
                raise SystemError("Echo pulse was not received")
        while GPIO.input(self.echo_pin) == 1:
            sonar_signal_on = time.time()

        time_passed = sonar_signal_on - sonar_signal_off
        return time_passed * ((self.speed_of_sound * 100) / 2)
