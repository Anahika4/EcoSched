
import psutil


def get_system_metrics():

    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # Get RAM information
    memory = psutil.virtual_memory()

    total_memory = memory.total / (1024 * 1024 * 1024)
    used_memory = memory.used / (1024 * 1024 * 1024)
    available_memory = memory.available / (1024 * 1024 * 1024)

    memory_usage = memory.percent

    # Get battery information, if available
    battery = psutil.sensors_battery()

    if battery is not None:
        battery_percentage = battery.percent

        if battery.power_plugged:
            charging_status = "Plugged In"
        else:
            charging_status = "On Battery"
    else:
        battery_percentage = None
        charging_status = "Not Available"

    metrics = {
        "cpu_usage": round(cpu_usage, 2),
        "memory_usage": round(memory_usage, 2),
        "total_memory": round(total_memory, 2),
        "used_memory": round(used_memory, 2),
        "available_memory": round(available_memory, 2),
        "battery_percentage": battery_percentage,
        "charging_status": charging_status
    }

    return metrics


if __name__ == "__main__":

    result = get_system_metrics()

    print("\n========== SYSTEM MONITOR ==========")

    print("CPU Usage:", result["cpu_usage"], "%")
    print("RAM Usage:", result["memory_usage"], "%")
    print("Total RAM:", result["total_memory"], "GB")
    print("Used RAM:", result["used_memory"], "GB")
    print("Available RAM:", result["available_memory"], "GB")

    print("Battery:", result["battery_percentage"])
    print("Charging Status:", result["charging_status"])
