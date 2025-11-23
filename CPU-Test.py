import multiprocessing
import time
import math
import psutil
import threading
import os
import sys
from datetime import datetime

# ====== COLOR CODES ======
RED     = "\033[31;1m"
GREEN   = "\033[32;1m"
YELLOW  = "\033[33;1m"
BLUE    = "\033[34;1m"
MAGENTA = "\033[35;1m"
CYAN    = "\033[36;1m"
RESET   = "\033[0m"
# ==========================

LOG_FILE = "cpu-test.log"
warning_shown = False

def write_log(text):
    with open(LOG_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {text}\n")

def stress_core(load_percentage, duration):
    end_time = time.time() + duration
    load_time = load_percentage / 100.0
    sleep_time = 1 - load_time

    while time.time() < end_time:
        start = time.time()

        while (time.time() - start) < load_time:
            math.sqrt(987654321)

        if sleep_time > 0:
            time.sleep(sleep_time)

def monitor_cpu(duration):
    global warning_shown
    end_time = time.time() + duration

    while time.time() < end_time:
        cpu = psutil.cpu_percent(interval=None)

        if cpu >= 80 and not warning_shown:
            msg = f"{RED}⚠ WARNING! High global CPU usage detected: {cpu}%{RESET}"
            print(msg)
            write_log(f"WARNING! High global CPU usage: {cpu}%")
            warning_shown = True
        time.sleep(1)

def countdown(duration):
    for i in range(duration, 0, -1):
        print(f"{CYAN}⏳ TIME REMAINING:{RESET} {i} seconds...", end="\r")
        time.sleep(1)
    print("\n")

def start_stress(cores_to_use, load_percentage, duration):
    total_threads = psutil.cpu_count(logical=True)
    approx_load = min(100, (cores_to_use * load_percentage / 100) / total_threads * 100)

    msg = (
        f"{GREEN}========================================={RESET}\n"
        f"{GREEN}Stress test starting...{RESET}\n"
        f"{GREEN}========================================={RESET}\n"
        f"{YELLOW}Configuration:{RESET}\n"
        f"  {CYAN}Processes (Cores) Used:{cores_to_use}{RESET}\n"
        f"  {CYAN}Load per process:   {load_percentage}%{RESET}\n"
        f"  {CYAN}Duration:           {duration} seconds{RESET}\n"
        f"{MAGENTA}Approx. Global Load:{RESET} {approx_load:.1f}% (Estimated)\n"
        f"{GREEN}========================================={RESET}\n"
    )
    print(msg)
    write_log(msg.replace("\033",""))

    monitor_thread = threading.Thread(target=monitor_cpu, args=(duration,))
    monitor_thread.start()

    timer_thread = threading.Thread(target=countdown, args=(duration,))
    timer_thread.start()

    processes = []
    for _ in range(cores_to_use):
        p = multiprocessing.Process(target=stress_core, args=(load_percentage, duration))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    monitor_thread.join()
    timer_thread.join()

    finish_msg = f"{GREEN}========================================={RESET}\n"
    finish_msg += f"{GREEN}Stress test successfully completed!{RESET}\n"
    finish_msg += f"{GREEN}========================================={RESET}"

    print(finish_msg)
    write_log("Stress test finished!")
    time.sleep(1)
    os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":

    total_cores = psutil.cpu_count(logical=False)
    total_threads = psutil.cpu_count(logical=True)

    os.system("clear" if os.name == 'posix' else 'cls')

    print(f"{BLUE}========================================={RESET}")
    print(f"{BLUE}======== {CYAN}CPU STRESS TEST V1.1{BLUE} ===========")
    print(f"{BLUE}========================================={RESET}")

    is_root = os.name == 'posix' and os.geteuid() == 0

    if is_root:
        print(f"{YELLOW}GitHub: {BLUE}https://github.com/ExnoxCH{RESET}")
        print(f"{YELLOW}(C) {CYAN}All reversed By Putra Maulana A{RESET}")
        print("\n" + f"{MAGENTA}--- SYSTEM INFORMATION ---{RESET}")
        print(f"{YELLOW}Logical CPUs (Threads):{RESET} {total_threads}")
        print(f"{YELLOW}Physical Cores:        {RESET} {total_cores}")
        print(f"{BLUE}--------------------------{RESET}")

    else:
        print(f"\n{RED}--- ROOT ACCESS REQUIRED ---{RESET}")
        print(f"{RED}This script requires root privileges (sudo) for stable operation and control.{RESET}")
        print(f"{YELLOW}Please exit and rerun using the command:{RESET}")
        print(f"{CYAN}sudo python3 {sys.argv[0]}{RESET}")
        print(f"{RED}----------------------------{RESET}\n")
        sys.exit(1)

    print(f"\n{RED}⚠ WARNING: Total CPU load should not exceed 100% per core!{RESET}\n")

    try:
        cores_to_use = int(input(f"{GREEN}1. Enter the number of processes (cores) to stress:{RESET} "))
        load_percentage = int(input(f"{GREEN}2. Enter CPU load percentage per core (1-100):{RESET} "))
        duration = int(input(f"{GREEN}3. Enter duration in seconds:{RESET} "))

        os.system('clear' if os.name == 'posix' else 'cls')

    except ValueError:
        print(f"{RED}\nInvalid input. Please enter valid numbers.{RESET}")
        sys.exit(1)

    if cores_to_use <= 0 or load_percentage <= 0 or duration <= 0:
        print(f"{RED}All values must be greater than zero.{RESET}")
        sys.exit(1)

    if load_percentage < 1 or load_percentage > 100:
        print(f"{RED}Error: CPU load percentage must be between 1 and 100.{RESET}")
        sys.exit(1)

    start_stress(cores_to_use, load_percentage, duration)
