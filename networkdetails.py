import socket
import subprocess
import platform
import urllib.parse
import re


def is_ipv4(ip_str):
    """Fungsi menyemak samada string itu adalah format IPv4 yang sah"""
    ip_pattern = r'^^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return bool(re.match(ip_pattern, ip_str.strip()))


def parse_windows_ipconfig():
    """Membaca ipconfig /all dan menapis hanya IPv4 untuk Gateway & DNS Server"""
    try:
        cmd = "ipconfig /all"
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')

        current_adapter = ""
        adapter_data = {}
        adapters = []

        lines = output.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            line_str = line.strip()

            # Mengesan nama adapter (cth: Wireless LAN adapter Wi-Fi:)
            if line and not line.startswith(" ") and ":" in line:
                if current_adapter and adapter_data:
                    adapters.append((current_adapter, adapter_data))
                    adapter_data = {}
                current_adapter = line.split(":")[0].strip()

            elif ":" in line_str:
                parts = line_str.split(":", 1)
                key = parts[0].replace(".", "").strip()
                val = parts[1].strip()

                if "IPv4 Address" in key or "IP Address" in key:
                    clean_val = val.replace("(Preferred)", "").strip()
                    if is_ipv4(clean_val):
                        adapter_data["IPv4 Address"] = clean_val

                elif "Subnet Mask" in key:
                    if is_ipv4(val):
                        adapter_data["Subnet Mask"] = val

                elif "Default Gateway" in key:
                    gateways = []
                    if val and is_ipv4(val):
                        gateways.append(val)
                    # Semak baris seterusnya jika ada multiple gateway
                    next_idx = i + 1
                    while next_idx < len(lines) and lines[next_idx].startswith(" ") and ":" not in lines[next_idx]:
                        next_val = lines[next_idx].strip()
                        if is_ipv4(next_val):
                            gateways.append(next_val)
                        next_idx += 1
                    if gateways:
                        adapter_data["Default Gateway"] = ", ".join(gateways)

                elif "DHCP Server" in key:
                    if is_ipv4(val):
                        adapter_data["DHCP Server"] = val

                elif "DNS Servers" in key:
                    dns_list = []
                    if val and is_ipv4(val):
                        dns_list.append(val)
                    # Semak baris seterusnya jika ada baris DNS tambahan
                    next_idx = i + 1
                    while next_idx < len(lines) and lines[next_idx].startswith(" ") and ":" not in lines[next_idx]:
                        next_val = lines[next_idx].strip()
                        if is_ipv4(next_val):
                            dns_list.append(next_val)
                        next_idx += 1
                    if dns_list:
                        adapter_data["DNS Server"] = ", ".join(dns_list)

            i += 1

        if current_adapter and adapter_data:
            adapters.append((current_adapter, adapter_data))

        # Paparkan adapter yang mempunyai IPv4 aktif sahaja
        active_found = False
        for adapter, data in adapters:
            if "IPv4 Address" in data:
                active_found = True
                print(f"--- [ {adapter} ] ---")
                print(f"  IPv4 Address    : {data.get('IPv4 Address', 'N/A')}")
                print(f"  Subnet Mask     : {data.get('Subnet Mask', 'N/A')}")
                print(f"  Default Gateway : {data.get('Default Gateway', 'None')}")
                print(f"  DHCP Server     : {data.get('DHCP Server', 'N/A')}")
                print(f"  DNS Server      : {data.get('DNS Server', 'N/A')}\n")

        if not active_found:
            print("Tiada sambungan IPv4 aktif dijumpai.\n")

    except Exception as e:
        print(f"Ralat membaca ipconfig: {e}")


def run_network_details(target_link):
    print("\n" + "=" * 55)
    print("       AMINOHYEAH TROUBLESHOOT: NETWORK DETAILS")
    print("=" * 55)
    print(f"Target Link Analyzed : {target_link}\n")

    # 1. NETWORK CONFIGURATION (IPV4 ONLY)
    print("=== [ LOCAL NETWORK CONFIGURATION (IPv4 ONLY) ] ===")
    parse_windows_ipconfig()

    # 2. TARGET LINK RESOLUTION
    print("=== [ TARGET LINK NETWORK CHECK ] ===")
    parsed_url = urllib.parse.urlparse(target_link)
    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
    print(f"Target Domain    : {domain}")

    try:
        target_ip = socket.gethostbyname(domain)
        print(f"Target IP        : {target_ip}")
    except Exception:
        print("Target IP        : Gagal mendapatkan IP (Offline/Invalid Domain)")

    print("\n" + "=" * 55)
    input("Tekan Enter untuk kembali ke menu utama...")


if __name__ == "__main__":
    test_link = "https://google.com"
    run_network_details(test_link)