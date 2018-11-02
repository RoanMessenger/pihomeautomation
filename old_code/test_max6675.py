from max6675 import MAX6675, MAX6675Error

cs_pin = 2
clock_pin = 3
data_pin = 4
units = "c"
thermocouple = MAX6675(cs_pin, clock_pin, data_pin, units)
print(thermocouple.get())
thermocouple.cleanup()
