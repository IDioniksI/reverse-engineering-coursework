from unicorn import *
from unicorn.x86_const import *
from capstone import *
from pwn import *

cs = Cs(CS_ARCH_X86, CS_MODE_64)
code = open("payload.bin", "rb").read()
address = 0


def hook_code(uc, address, size, user_data):
    global cs
    ins = uc.mem_read(address, size)
    print(f"Hook called at 0x{address:x}, instruction {ins.hex()}")
    for i in cs.disasm(ins, 0):
        if i.bytes.hex() == "e8e2ffffff":
            data = uc.mem_read(address + i.address + 5, len(code) - 36)
            modified_data = bytearray(data).replace(b"\x00", b"A").replace(
                b"\x05", b"B"
            )
            print(f"{modified_data}")
        if i.bytes.hex() == "cc":  # `int3`
            uc.emu_stop()


mu = Uc(UC_ARCH_X86, UC_MODE_64)
mu.mem_map(address, address + 0x2000)
mu.mem_write(address, code)
mu.reg_write(UC_X86_REG_ESP, address + 0x1000)
mu.hook_add(UC_HOOK_CODE, hook_code)

try:
    mu.emu_start(address, 36)
except UcError as e:
    print(f"Emulation error: {e}")

print("Done.")
