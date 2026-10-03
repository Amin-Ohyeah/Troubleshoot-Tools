import platform
import subprocess
import json
import psutil


def get_winsat_scores():
    """Tarik data skor WinSAT dari Windows menggunakan PowerShell"""
    if platform.system() != "Windows":
        return None, "Fungsi benchmark ini hanya disokong pada Windows."

    # Command PowerShell untuk dapatkan nilai WinSAT dalam format JSON
    ps_cmd = """
    $WinSAT = Get-CimInstance -ClassName Win32_WinSAT
    if ($WinSAT) {
        [PSCustomObject]@{
            CpuScore      = $WinSAT.CPUScore
            RamScore      = $WinSAT.MemoryScore
            GpuScore      = $WinSAT.GraphicsScore
            DiskScore     = $WinSAT.DiskScore
            BaseScore     = $WinSAT.WinSPRLevel
        } | ConvertTo-Json
    } else {
        "NOT_FOUND"
    }
    """

    try:
        output = subprocess.check_output(["powershell", "-Command", ps_cmd], stderr=subprocess.DEVNULL).decode(
            'utf-8').strip()
        if "NOT_FOUND" in output or not output:
            return None, "Data benchmark tidak dijumpai."

        scores = json.loads(output)
        return scores, None
    except Exception as e:
        return None, f"Ralat membaca WinSAT: {e}"


def run_checking_device(target_link):
    print("\n" + "=" * 55)
    print("      SISTEM SEMAKAN PERFORMANCE PC (CHECKING DEVICE)")
    print("=" * 55)
    print(f"Target Link Analyzed : {target_link}\n")

    # 1. SEMAKAN HARDWARE RINGKAS
    print("=== [ HARDWARE OVERVIEW ] ===")
    try:
        # Dapatkan Model PC
        cmd_model = 'powershell "(Get-CimInstance Win32_ComputerSystem).Manufacturer + \' - \' + (Get-CimInstance Win32_ComputerSystem).Model"'
        pc_model = subprocess.check_output(cmd_model, shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except Exception:
        pc_model = "Unknown Model"

    try:
        # Dapatkan Nama Processor
        cmd_cpu = 'powershell "(Get-CimInstance Win32_Processor).Name"'
        cpu_name = subprocess.check_output(cmd_cpu, shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except Exception:
        cpu_name = platform.processor() or "Unknown CPU"

    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    print(f"[+] Model PC   : {pc_model}")
    print(f"[+] Processor  : {cpu_name}")
    print(f"[+] Total RAM  : {ram_gb} GB")

    # 2. LAPORAN PRESTASI (BENCHMARK WINSAT)
    print("\n" + "=" * 55)
    print("          LAPORAN PRESTASI (BENCHMARK)          ")
    print("=" * 55)

    scores, error = get_winsat_scores()

    if error or not scores:
        print("[!] Data benchmark tidak dijumpai!")
        print(" -> Sila run command 'winsat formal' dahulu dalam PowerShell Admin.")
    else:
        cpu_s = scores.get('CpuScore', 0)
        ram_s = scores.get('RamScore', 0)
        gpu_s = scores.get('GpuScore', 0)
        disk_s = scores.get('DiskScore', 0)
        base_s = scores.get('BaseScore', 0)

        # Tukar peratusan (Skor / 9.9 * 100)
        perf_percent = round((base_s / 9.9) * 100)

        print(f" -> Prestasi Keseluruhan PC : {perf_percent}% (Skor Asas: {base_s} / 9.9)")
        print("    ----------------------------------------")
        print(f" -> Kuasa CPU        : {cpu_s} / 9.9")
        print(f" -> Kelajuan RAM     : {ram_s} / 9.9")
        print(f" -> Grafik (GPU)     : {gpu_s} / 9.9")
        print(f" -> Kelajuan Drive   : {disk_s} / 9.9")
        print("    ----------------------------------------")

        # 3. CADANGAN & STATUS UPGRADE
        print("\n[ Cadangan & Status Upgrade ]")

        if base_s >= 8.0:
            print(" [+] STATUS PC: SANGAT OK! PC anda dalam keadaan cemerlang. Tiada upgrade diperlukan.")
        else:
            print(" [!] STATUS PC: KURANG OK (Ada komponen lembap).")
            print("     Sila semak komponen dengan skor terendah di bawah:\n")

            if disk_s < 6.5:
                print(
                    f"     -> [TUKAR STORAGE]: Skor Storage anda ({disk_s}) rendah. Jika anda masih guna HDD, tukar kepada SSD (SATA atau NVMe). PC akan laju 10x ganda!")
            if ram_s < 6.5 or ram_gb < 8:
                print(
                    f"     -> [TAMBAH RAM]: Skor RAM anda ({ram_s}) rendah atau RAM kurang dari 8GB. Tambah RAM kepada minimum 8GB atau 16GB untuk hilangkan lag.")
            if cpu_s < 6.0:
                print(
                    f"     -> [CPU BOTTLENECK]: Processor anda sudah agak berusia. Komponen ini sukar ditukar (terutama laptop). Cadangan: Sedia bajet untuk PC baru.")
            if gpu_s < 6.0:
                print(
                    f"     -> [GRAFIK LEMBAP]: PC ini tidak sesuai untuk gaming berat atau video editing 4K. Sesuai untuk kerja pejabat sahaja.")

    print("\n" + "=" * 55)
    input("Tekan Enter untuk kembali ke menu utama...")


if __name__ == "__main__":
    test_link = "https://google.com"
    run_checking_device(test_link)