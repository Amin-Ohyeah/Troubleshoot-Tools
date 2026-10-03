import platform
import socket
import datetime
import subprocess
import psutil

# Import cpuinfo untuk dapatkan nama CPU yang bersih
try:
    import cpuinfo

    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False


def get_clean_processor_name():
    """Dapatkan nama CPU ringkas"""
    if HAS_CPUINFO:
        try:
            info = cpuinfo.get_cpu_info()
            if 'brand_raw' in info:
                return info['brand_raw']
        except Exception:
            pass
    raw_processor = platform.processor()
    if not raw_processor:
        return platform.machine()
    return raw_processor


def get_ram_details_windows():
    """Dapatkan Jenis RAM (DDR3/DDR4/DDR5) & Speed (MHz) menggunakan PowerShell"""
    ram_type = "Unknown"
    ram_speed = "Unknown"

    if platform.system() == "Windows":
        try:
            # Dapatkan MemoryType/SMBIOSMemoryType & Speed
            cmd = 'powershell "Get-CimInstance Win32_PhysicalMemory | Select-Object Speed, SMBIOSMemoryType"'
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8',
                                                                                                errors='ignore')

            speeds = []
            types = []

            # Kod pemetaan jenis RAM mengikut piawaian SMBIOS
            smbios_map = {
                20: "DDR", 21: "DDR2", 22: "DDR2 FB-DIMM",
                24: "DDR3", 26: "DDR4", 34: "DDR5"
            }

            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    speed_val = parts[0]
                    type_code = int(parts[1]) if parts[1].isdigit() else 0

                    speeds.append(f"{speed_val} MHz")
                    if type_code in smbios_map:
                        types.append(smbios_map[type_code])

            if speeds:
                ram_speed = ", ".join(list(set(speeds)))
            if types:
                ram_type = ", ".join(list(set(types)))
        except Exception:
            pass

    return ram_type, ram_speed


def get_size(bytes_size):
    """Tukar bytes kepada GB"""
    return f"{bytes_size / (1024 ** 3):.2f} GB"


def get_gpu_info():
    """Fungsi kesan GPU. Pulangkan 'None' jika tiada."""
    gpu_list = []

    if platform.system() == "Windows":
        try:
            cmd = "powershell Get-CimInstance -ClassName Win32_VideoController | Select-Name"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8',
                                                                                                errors='ignore')
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            for line in lines:
                if line.lower() not in ["name", "----", ""]:
                    gpu_list.append(line)
        except Exception:
            pass
    elif platform.system() == "Linux":
        try:
            cmd = "lspci | grep -E 'VGA|3D'"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8',
                                                                                                errors='ignore')
            for line in output.split('\n'):
                if line.strip():
                    gpu_name = line.split(" controller: ")[-1] if " controller: " in line else line
                    gpu_list.append(gpu_name.strip())
        except Exception:
            pass
    elif platform.system() == "Darwin":
        try:
            cmd = "system_profiler SPDisplaysDataType | grep 'Chipset Model'"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8',
                                                                                                errors='ignore')
            for line in output.split('\n'):
                if "Chipset Model:" in line:
                    gpu_list.append(line.split("Chipset Model:")[-1].strip())
        except Exception:
            pass

    return ", ".join(gpu_list) if gpu_list else "None"


def run_device_details(target_link):
    print("\n" + "=" * 50)
    print("       AMINOHYEAH TROUBLESHOOT: DEVICE DETAILS")
    print("=" * 50)
    print(f"Target Link Analyzed : {target_link}\n")

    # 1. SYSTEM & BOOT DETAILS (KEKAL)
    print("=== [ SYSTEM & BOOT DETAILS ] ===")
    print(f"OS System        : {platform.system()} {platform.release()} (v{platform.version()})")
    print(f"Hostname         : {socket.gethostname()}")
    print(f"Architecture     : {platform.architecture()[0]} ({platform.machine()})")

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    uptime = datetime.datetime.now() - bt
    print(f"System Boot Time : {bt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System Uptime    : {str(uptime).split('.')[0]} (Hours:Mins:Secs)")

    # 2. CPU DETAILS (SIMPLE: NAMA & TOTAL USAGE SAHAJA)
    print("\n=== [ CPU & GPU PERFORMANCE ] ===")
    print(f"Processor (CPU)  : {get_clean_processor_name()}")
    print(f"Total CPU Usage  : {psutil.cpu_percent(interval=1)}%")
    print(f"Graphics (GPU)   : {get_gpu_info()}")

    # 3. MEMORY DETAILS (SIMPLE: TOTAL MEMORY, JENIS RAM & SPEED)
    print("\n=== [ MEMORY / RAM STATUS ] ===")
    svmem = psutil.virtual_memory()
    ram_type, ram_speed = get_ram_details_windows()
    print(f"Total Memory     : {get_size(svmem.total)}")
    print(f"RAM Type         : {ram_type}")
    print(f"RAM Speed        : {ram_speed}")

    # 4. DISK & STORAGE DETAILS (SIMPLE: MOUNTPOINT & TOTAL SIZE SAHAJA)
    print("\n=== [ DISK DRIVES & STORAGE ] ===")
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            total_size = get_size(partition_usage.total)
        except PermissionError:
            total_size = "Access Denied"

        print(f"Drive ({partition.mountpoint:<3}) Total Size : {total_size}")

    print("\n" + "=" * 50)
    input("Tekan Enter untuk kembali ke menu utama...")


if __name__ == "__main__":
    test_link = "https://example.com"
    run_device_details(test_link)