import rpi_gpio


class Keypad:
    def __init__(self, characters, row_pins, col_pins):
        factory = rpi_gpio.KeypadFactory()
        self.keypad = factory.create_keypad(
            keypad=characters,
            row_pins=row_pins,
            col_pins=col_pins)
        self.pressed_keys = []
        self.keypad.registerKeyPressHandler(self.handle_key)

    def handle_key(self, key):
        self.pressed_keys.append(key)

    def get_keys(self):
        return self.pressed_keys

    def clear_keys(self):
        self.pressed_keys = []
