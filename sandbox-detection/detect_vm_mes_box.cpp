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

int main()
{
    if (IsVirtualMachine())
    {
        MessageBox(
            NULL, 
            "It's doesn't hello kitty", 
            "Detection environment", 
            MB_OK | MB_ICONINFORMATION
        );
    }
    else
    { 
        MessageBox( 
            NULL,  
            "Hello kitty!",  
            "Detection environment",  
            MB_OK | MB_ICONINFORMATION 
        ); 
    } 
    return 0;
}
