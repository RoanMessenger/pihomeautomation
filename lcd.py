import time
import RPi.GPIO as GPIO


class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7, chr_, cmd, chars, line_1, line_2):
        self.rs = rs
        self.e = e
        self.d4 = d4
        self.d5 = d5
        self.d6 = d6
        self.d7 = d7
        self.chr = chr_
        self.cmd = cmd
        self.chars = chars
        self.line_1 = line_1
        self.line_2 = line_2
        self.line_1_text = None
        self.line_2_text = None

        GPIO.setwarnings(False)
        GPIO.setup(e, GPIO.OUT)
        GPIO.setup(rs, GPIO.OUT)
        GPIO.setup(d4, GPIO.OUT)
        GPIO.setup(d5, GPIO.OUT)
        GPIO.setup(d6, GPIO.OUT)
        GPIO.setup(d7, GPIO.OUT)

        self.write(0x33, cmd)  # Initialize
        self.write(0x32, cmd)  # Set to 4-bit mode
        self.write(0x06, cmd)  # Cursor move direction
        self.write(0x0C, cmd)  # Turn cursor off
        self.write(0x28, cmd)  # 2 line display
        self.write(0x01, cmd)  # Clear display
        time.sleep(0.0005)  # Delay to allow commands to process

    def write(self, bits, mode):
        # High bits
        GPIO.output(self.rs, mode)  # RS

        GPIO.output(self.d4, False)
        GPIO.output(self.d5, False)
        GPIO.output(self.d6, False)
        GPIO.output(self.d7, False)
        if bits & 0x10 == 0x10:
            GPIO.output(self.d4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.d5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.d6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.d7, True)

        # Toggle 'Enable' pin
        self.toggle_enable()

        # Low bits
        GPIO.output(self.d4, False)
        GPIO.output(self.d5, False)
        GPIO.output(self.d6, False)
        GPIO.output(self.d7, False)
        if bits & 0x01 == 0x01:
            GPIO.output(self.d4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.d5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.d6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.d7, True)

        # Toggle 'Enable' pin
        self.toggle_enable()

    def toggle_enable(self):
        time.sleep(0.0005)
        GPIO.output(self.e, True)
        time.sleep(0.0005)
        GPIO.output(self.e, False)
        time.sleep(0.0005)

    def text(self, message, line):
        # Send text to display
        message = message.ljust(self.chars, " ")

        self.write(line, self.cmd)

        for i in range(self.chars):
            self.write(ord(message[i]), self.chr)

    def write_both(self, line_1_text, line_2_text):
        if line_1_text != self.line_1_text:
            self.text(line_1_text, self.line_1)
            self.line_1_text = line_1_text
        if line_2_text != self.line_2_text:
            self.text(line_2_text, self.line_2)
            self.line_2_text = line_2_text
