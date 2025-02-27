
# ! pip install furiosa-smi-py

import furiosa_smi_py
from furiosa_smi_py import init, list_devices
import time

init()

def print_device_info_params(i:int, device: furiosa_smi_py.Device) -> None:
    device_info = device.device_info() # Acquire information about the NPU device.
    print(f"Device Info #{i}")
    print(f"\t\tDevice Arch: {device_info.arch()}")
    print(f"\t\tDevice Cores: {device_info.core_num()}")
    print(f"\t\tDevice Firmware Version: {device_info.firmware_version()}")
    print(f"\t\tDevice Pert Version: {device_info.pert_version()}")



def get_device_power_consumption(device: furiosa_smi_py.Device) -> float:
    device_power_consumption = device.power_consumption()
    # print(f"Device Power Consumption: {device_power_consumption}")
    return device_power_consumption

def get_temperature_params(device: furiosa_smi_py.Device) -> tuple[float, float]:
    device_temperature = device.device_temperature()
    # print(f"Device Ambient Temperature: {device_temperature.ambient()}")
    # print(f"Device SoC Peak Temperature: {device_temperature.soc_peak()}")
    return device_temperature.ambient(), device_temperature.soc_peak()

def get_core_utilization_params(device: furiosa_smi_py.Device):
    core_utilization = device.core_utilization()
    
    pe_utilization = core_utilization.pe_utilization()
    pe_utilization_list = []
    for i in range(8):
        pe_utilization_list.append(pe_utilization[i].pe_usage_percentage())
    avg_pe_utilization = sum(pe_utilization_list) / len(pe_utilization_list)
    return avg_pe_utilization

if __name__ == "__main__":
    import csv
    from datetime import datetime

    devices = list_devices() # Retrieve a list of NPU devices in the system.
    print(f'Devices count: {len(devices)}')
    for i, device in enumerate(devices):
        print_device_info_params(i, device)

    
    csv_filename = f"npu_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    time_interval = 2 # seconds 
    
    # Create and write headers to CSV file
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Timestamp', 'Ambient Temperature', 'SoC Peak Temperature', 
                          'Power Consumption', 'Average PE Utilization'])
    
    print(f"Monitoring started by user at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Data is being saved to: {csv_filename}")
    
    try:
        while True:
            print("\n" + "="*50)
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Timestamp: {current_time}")
            
            for device in devices:
                ambient_temperature, soc_peak_temperature = get_temperature_params(device)
                power_consumption = get_device_power_consumption(device)
                avg_pe_utilization = get_core_utilization_params(device)
                
                # Print to console
                print(f"Ambient Temperature: {ambient_temperature:0.2f}")
                print(f"SoC Peak Temperature: {soc_peak_temperature:0.2f}")
                print(f"Device Power Consumption: {power_consumption:0.2f}")
                print(f"Average PE Utilization: {avg_pe_utilization:0.2f}")
                
                # Write to CSV
                with open(csv_filename, 'a', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow([current_time, ambient_temperature, 
                                      soc_peak_temperature, power_consumption, 
                                      avg_pe_utilization])
                    
            time.sleep(time_interval)
            
    except KeyboardInterrupt:
        print(f"\nMonitoring stopped by user at {time.strftime('%Y-%m-%d %H:%M:%S')}")
