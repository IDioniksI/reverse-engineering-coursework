# Reverse Engineering and Malware Analysis

This repository contains selected practical work from a university course on reverse engineering and malware analysis. It focuses on small research prototypes and analysis utilities rather than production-ready security tools.

## Contents

| Project | Description |
| --- | --- |
| [Deobfuscation](deobfuscation/) | Static byte-pattern analysis and dynamic x86-64 payload emulation with Unicorn and Capstone. |
| [Sandbox Detection](sandbox-detection/) | CPUID-based hypervisor detection and experiments with executing an embedded payload. |
| [Remote Control System](remote-control-system/) | A Python client-server prototype used to study remote-control behavior and related host capabilities. |
| [Network Traffic Interception](network-traffic-interception/) | Linux traffic interception and modification experiments using iptables, NetfilterQueue, and Scapy. |
| [Memory and Antivirus Analysis](memory-and-antivirus-analysis/) | Windows process-memory parsing and experiments with antivirus detection as an analysis oracle. |
| [JavaScript Deobfuscation](javascript-deobfuscation/) | Utilities for inspecting obfuscated JavaScript/JScript and extracting embedded compressed data. |
| [Android Reverse Engineering](android-reverse-engineering/) | Frida hooks and supporting scripts for studying runtime behavior and protection checks in Android applications. |

Each directory has its own README with a description of the included files, their responsibilities, and any project-specific usage notes.

## Technologies

- Python, C/C++, and JavaScript
- Unicorn Engine and Capstone
- Frida and Android runtime instrumentation
- Windows API and process-memory inspection
- Scapy, NetfilterQueue, and iptables
- Static analysis, emulation, deobfuscation, and runtime behavior analysis

## Repository Notes

The code is preserved close to its original coursework form, with documentation added to make the purpose of each file clear. Some projects are intentionally small or experimental and may depend on a specific operating system, architecture, vulnerable test application, or lab environment.

No malware samples, third-party application binaries, or compiled payloads are distributed in this repository.

## Responsible Use

Some examples demonstrate security-sensitive behavior, including payload execution, traffic modification, process-memory inspection, and remote-control functionality. They are provided strictly for educational research in isolated environments and on systems where explicit authorization has been granted.
