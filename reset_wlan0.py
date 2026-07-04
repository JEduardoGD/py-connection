import subprocess

def reset_wlan0():
    command = "sudo ip link set wlan0 down && sleep 5 && sudo ip link set wlan0 up"
    try:
        print(f"Executing: {command}")
        # Using shell=True because of the '&&' operator
        subprocess.run(command, shell=True, check=True)
        print("wlan0 reset successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

if __name__ == "__main__":
    reset_wlan0()
