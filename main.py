import sys
import os

# Import modul mengikut nama fail sebenar
import devicedetails
import networkdetails
import checkdevice


def clear_screen():
    """Bersihkan paparan terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_menu():
    print("==============================================")
    print("        AMINOHYEAH TROUBLESHOOT TOOL          ")
    print("==============================================")
    print("1. Device details")
    print("2. Network details")
    print("3. Checking device")
    print("0. Exit")


def get_target_link():
    """Minta link target bila pengguna pilih menu 1, 2, atau 3"""
    link = input("\nMasukkan link/URL target: ").strip()
    while not link:
        print("Link tidak boleh kosong!")
        link = input("Masukkan link/URL target: ").strip()

    if not link.startswith(('http://', 'https://')):
        link = 'https://' + link
    return link


def main():
    while True:
        clear_screen()
        show_menu()
        choice = input("\nPilih menu [0-3]: ").strip()

        if choice == "1":
            target_link = get_target_link()
            devicedetails.run_device_details(target_link)
        elif choice == "2":
            target_link = get_target_link()
            networkdetails.run_network_details(target_link)
        elif choice == "3":
            target_link = get_target_link()
            checkdevice.run_checking_device(target_link)
        elif choice == "0":
            print("\nTerima kasih menggunakan Aminohyeah Troubleshoot. Keluar...")
            sys.exit()
        else:
            input("\nPilihan tidak sah! Tekan Enter untuk cuba lagi...")


if __name__ == "__main__":
    main()