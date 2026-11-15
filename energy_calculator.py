
from battery_manager import get_power_mode


def calculate_energy(burst_time, mode):
    ans = get_power_mode(mode)

    if ans == None:
        return None

    speed = ans[0]
    power = ans[1]

    execution_time = burst_time / speed
    energy = power * execution_time

    return execution_time, energy


if __name__ == "__main__":
    burst_time = 4
    mode = "Medium"

    ans = calculate_energy(burst_time, mode)

    if ans != None:
        print("Execution Time:", ans[0])
        print("Energy:", ans[1])
