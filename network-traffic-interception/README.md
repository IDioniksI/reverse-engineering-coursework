# Network Traffic Interception Tools

Python and Linux networking examples for inspecting and modifying an
unencrypted TCP command protocol, together with a reduced sinkhole controller
for the remote control prototype.

## Files

### `iptables.sh`

Configures a Linux host for traffic forwarding:

- enables IPv4 forwarding;
- adds source NAT masquerading on `eth0`;
- redirects TCP ports `80` and `443` to local port `8080`.

The redirect rules are suitable for a separately configured interception proxy.

The interface name and existing firewall state are not detected automatically.
Review the rules before running the script on a test gateway.

### `mitm.py`

A Scapy and NetfilterQueue packet handler for the unencrypted command protocol
on TCP port `9999`.

`modify()` performs the following operations:

1. Parses the queued packet as an IPv4 packet.
2. Selects TCP traffic where either endpoint uses port `9999`.
3. Inspects packets containing a raw payload.
4. Replaces an exact controller command `2` with command `3` when it is being
   sent to port `9999`.
5. Removes the cached IP length and IP/TCP checksums so Scapy recalculates them.
6. Returns the modified packet to the network stack.

In the associated command protocol, this changes a system-information request
into a directory-listing request.

The script binds to NFQUEUE number `1`. A matching firewall rule must be
configured separately before packets will reach the handler.

The handler also assumes that the traffic already passes through the Linux
host. In the original isolated network setup, this was achieved with ARP
spoofing followed by IP forwarding. ARP spoofing itself is not implemented by
any file in this directory.

### `server_cut.py`

A reduced controller compatible with the endpoint from the remote control
prototype.

Implemented functions:

- `save_file()` — receives a size-prefixed file;
- `list_dir()` — displays a remote directory listing;
- `open_dir()` — changes the current directory on the endpoint;
- `search_file()` — requests a search for `client.exe` and returns the first
  result;
- `interactive_shell()` — sends a Windows command that terminates
  `client.exe` and deletes it from a hard-coded path;
- `main()` — connects to `192.168.1.10:9999` and provides a reduced command
  menu.

When command `2` is selected, the controller first receives system information,
then enters the endpoint's shell mode and sends the process-termination and
file-deletion command.

## Requirements

`mitm.py` requires:

- Linux with NetfilterQueue support;
- Python 3;
- Scapy;
- the Python NetfilterQueue bindings and their system library;
- root privileges for firewall and packet-queue configuration.

Install the Python packages after the system NetfilterQueue development library
is available:

```bash
python -m pip install scapy NetfilterQueue
```

`server_cut.py` uses only the Python standard library, but it requires a
compatible endpoint listening on TCP port `9999`.

## Configuration

Before use, review and update:

- the network interface `eth0` in `iptables.sh`;
- the endpoint address `192.168.1.10` in `server_cut.py`;
- the hard-coded Windows path in `interactive_shell()`;
- the firewall rule that sends the intended packets to NFQUEUE number `1`.

The included firewall commands represent two related but separate setups:

- IP forwarding and masquerading allow the Linux host to act as a gateway
  after traffic has been redirected through it;
- the port `80` and `443` redirects target a local interception proxy on port
  `8080`;
- `mitm.py` operates on port `9999` traffic delivered through NFQUEUE `1`, which
  requires an additional rule not present in `iptables.sh`.

## Safety

These files can modify live network traffic and delete the remote client
executable. Use them only on systems and networks you own or are explicitly
authorized to test. Run them in an isolated environment and review all firewall
rules and hard-coded paths first.
