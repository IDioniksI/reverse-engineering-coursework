import winappdbg
from winappdbg import win32
import re

system = winappdbg.System()
system.request_debug_privileges()
system.scan_processes()

program_name = "client.exe"
print "\nStarted parsing:", program_name

for process, process_name in system.find_processes_by_filename(program_name):
    process_id = process.get_pid()
    architecture_bits = process.get_bits()
    print "PID:", process_id, "         ", architecture_bits, "bits"

    memory_map = process.get_memory_map()
    for memory_region in memory_map:
        base_address = memory_region.BaseAddress
        if memory_region.has_content():
            region_size = memory_region.RegionSize
            memory_data = process.read(base_address, region_size)

            ip_addresses = re.findall(r"192\.\d{1,3}\.\d{1,3}\.\d{1,3}", memory_data)
            if len(ip_addresses) > 0:
                print "Connected to server:", ip_addresses
