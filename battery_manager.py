def get_power_mode(mode):

    if mode == "Low":
        speed = 0.5
        power = 2

    elif mode == "Medium":
        speed = 1
        power = 5

    elif mode == "High":
        speed = 2
        power = 12

    else:
        print("Invalid power mode")
        return None

    return speed, power
