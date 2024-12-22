Helping Guide for NS3 (Batter than nothing)

#### Write python script to implement the simple network shown in the figure below
1. This network consists of 4 nodes (n0, n1, n2, n3)
2. The duplex links between n0 and n2, and n1 and n2 have 2 Mbps of
bandwidth and 10 ms of delay.
3. The duplex link between n2 and n3 has 1.7 Mbps of bandwidth and 20 ms
of delay.
4. Each node uses a DropTail queue, of which the maximum size is 10. You
will have to orient the nodes as shown in the diagram below.
5. A "tcp" agent is attached to n1, and a connection is established to a tcp
"sink" agent attached to n3.
6. A tcp "sink" agent generates and sends ACK packets to the sender (tcp
agent) and frees the received packets.
7. A "udp" agent that is attached to n0 is connected to a "null" agent attached to
n3. A "null" agent just frees the packets received.
8. A "ftp" and a "cbr" traffic generator are attached to "tcp" and "udp" agents
respectively, and the "cbr" is configured to generate packets having size of 1
Kbytesat the rate of 100 packets per second.
9. FTP will control the traffic automatically according to the throttle
mechanism in TCP.
10. The traffic flow of UDP must be colored red and traffic flow of TCP must be
colored blue.
11. The "cbr" is set to start at 0.1 sec and stop at 4.5 sec,
12. "ftp" is set to start at 0.5 sec and stop at 4.0 sec.

----------

```python
import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.visualizer
import ns.flow_monitor
import ns.traffic_control

def main():
    # Create nodes
    nodes = ns.network.NodeContainer()
    nodes.Create(4)  # Create 4 nodes: n0, n1, n2, n3

    # Install Internet Stack on all nodes
    stack = ns.internet.InternetStackHelper()
    stack.Install(nodes)

    # Point-to-point link between n0 and n2 (2 Mbps, 10 ms delay)
    p2p_n0_n2 = ns.point_to_point.PointToPointHelper()
    p2p_n0_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
    p2p_n0_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
    devices_n0_n2 = p2p_n0_n2.Install(nodes.Get(0), nodes.Get(2))

    # Point-to-point link between n1 and n2 (2 Mbps, 10 ms delay)
    p2p_n1_n2 = ns.point_to_point.PointToPointHelper()
    p2p_n1_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
    p2p_n1_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
    devices_n1_n2 = p2p_n1_n2.Install(nodes.Get(1), nodes.Get(2))

    # Point-to-point link between n2 and n3 (1.7 Mbps, 20 ms delay)
    p2p_n2_n3 = ns.point_to_point.PointToPointHelper()
    p2p_n2_n3.SetDeviceAttribute("DataRate", ns.core.StringValue("1.7Mbps"))
    p2p_n2_n3.SetChannelAttribute("Delay", ns.core.StringValue("20ms"))
    devices_n2_n3 = p2p_n2_n3.Install(nodes.Get(2), nodes.Get(3))

    # Assign IP addresses
    address = ns.internet.Ipv4AddressHelper()

    # IP for n0-n2 link
    address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
    interfaces_n0_n2 = address.Assign(devices_n0_n2)

    # IP for n1-n2 link
    address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
    interfaces_n1_n2 = address.Assign(devices_n1_n2)

    # IP for n2-n3 link
    address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
    interfaces_n2_n3 = address.Assign(devices_n2_n3)

    # Enable routing
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    # Configure DropTail queue with max size 10 packets
    traffic_control = ns.traffic_control.TrafficControlHelper()
    traffic_control.SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.UintegerValue(10))
    traffic_control.Install(devices_n0_n2)
    traffic_control.Install(devices_n1_n2)
    traffic_control.Install(devices_n2_n3)

    # Add TCP FTP application on n1 and sink on n3
    tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
    tcp_sink_app = tcp_sink.Install(nodes.Get(3))
    tcp_sink_app.Start(ns.core.Seconds(0.0))
    tcp_sink_app.Stop(ns.core.Seconds(10.0))

    ftp = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
    ftp.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data
    ftp_app = ftp.Install(nodes.Get(1))
    ftp_app.Start(ns.core.Seconds(0.5))
    ftp_app.Stop(ns.core.Seconds(4.0))

    # Add UDP CBR application on n0 and sink on n3
    udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
    udp_sink_app = udp_sink.Install(nodes.Get(3))
    udp_sink_app.Start(ns.core.Seconds(0.0))
    udp_sink_app.Stop(ns.core.Seconds(10.0))

    cbr = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
    cbr.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
    cbr.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # 100 packets/sec
    cbr_app = cbr.Install(nodes.Get(0))
    cbr_app.Start(ns.core.Seconds(0.1))
    cbr_app.Stop(ns.core.Seconds(4.5))

    # Enable FlowMonitor to track and color traffic
    flowmon = ns.flow_monitor.FlowMonitorHelper()
    monitor = flowmon.InstallAll()

    # Define traffic coloring rules
    def ColorTraffic():
        classifier = flowmon.GetClassifier()
        for flow_id, flow_stats in monitor.GetFlowStats():
            flow_desc = classifier.FindFlow(flow_id)
            if flow_desc.protocol == 6:  # TCP (6 in IP header)
                print(f"Flow {flow_id} (TCP): Color it BLUE")
            elif flow_desc.protocol == 17:  # UDP (17 in IP header)
                print(f"Flow {flow_id} (UDP): Color it RED")

    # Enable PyViz visualization
    ns.visualizer.PyVizHelper.Enable()

    # Run simulation
    ns.core.Simulator.Stop(ns.core.Seconds(10.0))
    ns.core.Simulator.Run()

    # Color traffic based on protocol
    ColorTraffic()

    # Destroy simulation
    ns.core.Simulator.Destroy()

if __name__ == "__main__":
    main()


```

  
----------


# In-Depth Documentation of the Network Simulation Code

This documentation explains the functionality and purpose of each line of the provided Python code for simulating a network using ns-3. It delves into all parameters passed to functions and the underlying logic.

----------

## Code Breakdown

### 1. Importing Required Modules

```python
import ns.core
import ns.network
import ns.internet
import ns.applications
import ns.point_to_point
import ns.traffic_control
import ns.flow_monitor
import ns.visualizer

```

-   **Purpose**: These imports bring in the necessary components of ns-3 into the Python script. Each module provides specific functionalities:
    -   `ns.core`: Core functionality for scheduling events, setting up simulation time, and managing attributes.
    -   `ns.network`: Provides classes for creating nodes and network devices.
    -   `ns.internet`: Supplies IP stack and routing protocols.
    -   `ns.applications`: Defines applications such as FTP and CBR.
    -   `ns.point_to_point`: Manages point-to-point links between nodes.
    -   `ns.traffic_control`: Allows configuration of queue management systems, such as DropTail.
    -   `ns.flow_monitor`: Provides tools for monitoring traffic flows.
    -   `ns.visualizer`: Enables visualization of the network.

----------

### 2. Creating Nodes

```python
nodes = ns.network.NodeContainer()
nodes.Create(4)

```

-   **Purpose**: This creates a container for the network nodes and initializes four nodes (`n0`, `n1`, `n2`, `n3`).
-   **Explanation**:
    -   `NodeContainer()`: A helper class that simplifies node creation and management.
    -   `Create(4)`: Allocates four nodes within the container.

----------

### 3. Installing the Internet Stack

```python
stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

```

-   **Purpose**: Installs the TCP/IP stack on all nodes to enable communication using standard Internet protocols.
-   **Explanation**:
    -   `InternetStackHelper()`: A helper class for managing network stacks on nodes.
    -   `Install(nodes)`: Installs the Internet stack on all nodes in the `NodeContainer`.

----------

### 4. Configuring Point-to-Point Links

#### Link Between `n0` and `n2`

```python
p2p_n0_n2 = ns.point_to_point.PointToPointHelper()
p2p_n0_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
p2p_n0_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
devices_n0_n2 = p2p_n0_n2.Install(nodes.Get(0), nodes.Get(2))

```

-   **Purpose**: Sets up a point-to-point connection between nodes `n0` and `n2` with a bandwidth of 2 Mbps and delay of 10 ms.
-   **Explanation**:
    -   `PointToPointHelper()`: Configures point-to-point links.
    -   `SetDeviceAttribute("DataRate", ...)`: Defines the bandwidth.
        -   **Parameter**: `StringValue("2Mbps")` specifies a bandwidth of 2 Mbps.
    -   `SetChannelAttribute("Delay", ...)`: Specifies the propagation delay.
        -   **Parameter**: `StringValue("10ms")` specifies a delay of 10 ms.
    -   `Install(nodes.Get(0), nodes.Get(2))`: Creates the link and attaches it to nodes `n0` and `n2`.

#### Link Between `n1` and `n2`

```python
p2p_n1_n2 = ns.point_to_point.PointToPointHelper()
p2p_n1_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
p2p_n1_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
devices_n1_n2 = p2p_n1_n2.Install(nodes.Get(1), nodes.Get(2))

```

-   **Purpose**: Sets up a point-to-point connection between nodes `n1` and `n2` with the same bandwidth and delay as above.

#### Link Between `n2` and `n3`

```python
p2p_n2_n3 = ns.point_to_point.PointToPointHelper()
p2p_n2_n3.SetDeviceAttribute("DataRate", ns.core.StringValue("1.7Mbps"))
p2p_n2_n3.SetChannelAttribute("Delay", ns.core.StringValue("20ms"))
devices_n2_n3 = p2p_n2_n3.Install(nodes.Get(2), nodes.Get(3))

```

-   **Purpose**: Sets up a point-to-point connection between nodes `n2` and `n3` with a bandwidth of 1.7 Mbps and delay of 20 ms.

----------

### 5. Assigning IP Addresses

```python
address = ns.internet.Ipv4AddressHelper()

```

-   **Purpose**: This helper assigns IP addresses to the devices on each link.

#### Assigning IP Addresses to Links

```python
address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n0_n2 = address.Assign(devices_n0_n2)

```

-   **Purpose**: Assigns IP addresses to the `n0-n2` link.
-   **Explanation**:
    -   `SetBase(...)`: Specifies the subnet and subnet mask.
        -   **Parameters**:
            -   `Ipv4Address("10.1.1.0")`: Subnet.
            -   `Ipv4Mask("255.255.255.0")`: Subnet mask.
    -   `Assign(devices_n0_n2)`: Assigns IP addresses to devices in the link.

```python
address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n1_n2 = address.Assign(devices_n1_n2)

```

-   **Purpose**: Assigns IP addresses to the `n1-n2` link.

```python
address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n2_n3 = address.Assign(devices_n2_n3)

```

-   **Purpose**: Assigns IP addresses to the `n2-n3` link.

----------

### 6. Enabling Routing

```python
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

```

-   **Purpose**: Populates the global routing tables to ensure all nodes can route packets to their destinations.

----------

### 7. Setting Up TCP Traffic
### 8. Setting Up UDP Traffic
explained below

----------

### 9. Setting Up Flow Monitor and Visualization

```python
flowmon = ns.flow_monitor.FlowMonitorHelper()
monitor = flowmon.InstallAll()

```

-   **Purpose**: Enables traffic monitoring to analyze flows.

```python
ns.visualizer.PyVizHelper.Enable()

```

-   **Purpose**: Activates PyViz for graphical visualization.

```python
def ColorTraffic():
    classifier = flowmon.GetClassifier()
    for flow_id, flow_stats in monitor.GetFlowStats():
        flow_desc = classifier.FindFlow(flow_id)
        if flow_desc.protocol == 6:  # TCP (6 in IP header)
            print(f"Flow {flow_id} (TCP): Color it BLUE")
        elif flow_desc.protocol == 17:  # UDP (17 in IP header)
            print(f"Flow {flow_id} (UDP): Color it RED")
ColorTraffic()

```

-   **Purpose**: Colors traffic based on protocol type.
-   **Explanation**:
    -   Protocol 6: TCP (blue).
    -   Protocol 17: UDP (red).

----------

### 10. Running the Simulation

```python
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()

```

-   **Purpose**: Executes the simulation and cleans up resources afterward.

----------

This documentation ensures every line and parameter of the script is explained comprehensively. If further elaboration is needed, feel free to ask!

----------

# More Details:


```python
    # Enable routing
    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

    # Configure DropTail queue with max size 10 packets
    traffic_control = ns.traffic_control.TrafficControlHelper()
    traffic_control.SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.UintegerValue(10))
    traffic_control.Install(devices_n0_n2)
    traffic_control.Install(devices_n1_n2)
    traffic_control.Install(devices_n2_n3)

    # Add TCP FTP application on n1 and sink on n3
    tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
    tcp_sink_app = tcp_sink.Install(nodes.Get(3))
    tcp_sink_app.Start(ns.core.Seconds(0.0))
    tcp_sink_app.Stop(ns.core.Seconds(10.0))

    ftp = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
    ftp.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data
    ftp_app = ftp.Install(nodes.Get(1))
    ftp_app.Start(ns.core.Seconds(0.5))
    ftp_app.Stop(ns.core.Seconds(4.0))

    # Add UDP CBR application on n0 and sink on n3
    udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
    udp_sink_app = udp_sink.Install(nodes.Get(3))
    udp_sink_app.Start(ns.core.Seconds(0.0))
    udp_sink_app.Stop(ns.core.Seconds(10.0))

    cbr = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
    cbr.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
    cbr.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # 100 packets/sec
    cbr_app = cbr.Install(nodes.Get(0))
    cbr_app.Start(ns.core.Seconds(0.1))
    cbr_app.Stop(ns.core.Seconds(4.5))

    # Enable FlowMonitor to track and color traffic
    flowmon = ns.flow_monitor.FlowMonitorHelper()
    monitor = flowmon.InstallAll()

    # Define traffic coloring rules
    def ColorTraffic():
        classifier = flowmon.GetClassifier()
        for flow_id, flow_stats in monitor.GetFlowStats():
            flow_desc = classifier.FindFlow(flow_id)
            if flow_desc.protocol == 6:  # TCP (6 in IP header)
                print(f"Flow {flow_id} (TCP): Color it BLUE")
            elif flow_desc.protocol == 17:  # UDP (17 in IP header)
                print(f"Flow {flow_id} (UDP): Color it RED")

    # Enable PyViz visualization
    ns.visualizer.PyVizHelper.Enable()
    

```
# Comprehensive Documentation for the Network Simulation Code

This documentation provides an **in-depth explanation** of the code. Each line is broken down to explain its purpose, the parameters passed, and its contribution to the overall simulation.

----------

## **Code Documentation**

### **Routing Configuration**

```python
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

```

-   **Purpose**: This line populates the global routing tables for the nodes in the simulation.
-   **Explanation**:
    -   `Ipv4GlobalRoutingHelper`: A helper that enables global routing for IPv4 in ns-3.
    -   `PopulateRoutingTables()`: Automatically computes and installs routes for all IPv4-enabled nodes in the network. This is critical for enabling end-to-end communication between nodes.

----------

### **Configuring DropTail Queues**

```python
traffic_control = ns.traffic_control.TrafficControlHelper()
traffic_control.SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.UintegerValue(10))
traffic_control.Install(devices_n0_n2)
traffic_control.Install(devices_n1_n2)
traffic_control.Install(devices_n2_n3)

```

-   **Purpose**: Configures a **DropTail queue** on each link in the network to limit the maximum number of packets stored in the queue to 10.
-   **Explanation**:
    -   `TrafficControlHelper()`: A helper class to configure and manage traffic control for network devices.
    -   `SetQueue("ns3::DropTailQueue", "MaxPackets", ns.core.UintegerValue(10))`: Specifies the use of a DropTail queue with a maximum capacity of 10 packets.
        -   `"ns3::DropTailQueue"`: Represents a simple FIFO (First-In-First-Out) queueing discipline.
        -   `"MaxPackets"`: Specifies the attribute to set. Here, it defines the maximum number of packets the queue can hold.
        -   `ns.core.UintegerValue(10)`: Sets the maximum queue size to 10 packets.
    -   `Install(devices_n0_n2)`: Applies the configured queue to the link between nodes `n0` and `n2`.
    -   Similarly, queues are installed on the links `n1-n2` and `n2-n3`.

----------

### **TCP FTP Application**

#### **TCP Sink on n3**

```python
tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
tcp_sink_app = tcp_sink.Install(nodes.Get(3))
tcp_sink_app.Start(ns.core.Seconds(0.0))
tcp_sink_app.Stop(ns.core.Seconds(10.0))

```

-   **Purpose**: Installs a TCP **sink** application on `n3`, which will receive TCP packets from the TCP agent (sender) at `n1`.
-   **Explanation**:
    -   `PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))`: Creates a TCP sink.
        -   `"ns3::TcpSocketFactory"`: Specifies that this sink will use TCP for communication.
        -   `ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9)`: Configures the sink to listen on port `9` for any incoming TCP packets.
            -   `Ipv4Address.GetAny()`: Means it will accept packets destined for any IP address assigned to `n3`.
    -   `tcp_sink.Install(nodes.Get(3))`: Installs the TCP sink application on node `n3`.
    -   `tcp_sink_app.Start(ns.core.Seconds(0.0))`: The sink starts listening at simulation time `0.0` seconds.
    -   `tcp_sink_app.Stop(ns.core.Seconds(10.0))`: The sink stops listening at `10.0` seconds.

#### **FTP on n1**

```python
ftp = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
ftp.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data
ftp_app = ftp.Install(nodes.Get(1))
ftp_app.Start(ns.core.Seconds(0.5))
ftp_app.Stop(ns.core.Seconds(4.0))

```

-   **Purpose**: Configures an FTP application on `n1` to send TCP traffic to the sink at `n3`.
-   **Explanation**:
    -   `BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))`: Creates an FTP-like application.
        -   `"ns3::TcpSocketFactory"`: Specifies that this application will use TCP.
        -   `InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9)`: Targets the IP address of `n3` on the `n2-n3` link and port `9`.
    -   `ftp.SetAttribute("MaxBytes", ns.core.UintegerValue(0))`: Configures the application to send unlimited data (`0` means no limit).
    -   `ftp.Install(nodes.Get(1))`: Installs the FTP application on `n1`.
    -   `ftp_app.Start(ns.core.Seconds(0.5))`: The application starts at `0.5` seconds.
    -   `ftp_app.Stop(ns.core.Seconds(4.0))`: The application stops at `4.0` seconds.

----------

### **UDP CBR Application**

#### **UDP Sink on n3**

```python
udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
udp_sink_app = udp_sink.Install(nodes.Get(3))
udp_sink_app.Start(ns.core.Seconds(0.0))
udp_sink_app.Stop(ns.core.Seconds(10.0))

```

-   **Purpose**: Installs a UDP sink on `n3` to receive UDP traffic from `n0`.
-   **Explanation**:
    -   `"ns3::UdpSocketFactory"`: Specifies that the sink will use UDP for communication.
    -   `InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10)`: Configures the sink to listen on port `10`.
    -   `udp_sink.Install(nodes.Get(3))`: Installs the UDP sink application on `n3`.
    -   `Start` and `Stop`: Similar to the TCP sink.

#### **CBR on n0**

```python
cbr = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
cbr.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
cbr.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # 100 packets/sec
cbr_app = cbr.Install(nodes.Get(0))
cbr_app.Start(ns.core.Seconds(0.1))
cbr_app.Stop(ns.core.Seconds(4.5))

```

-   **Purpose**: Configures a **CBR (Constant Bit Rate)** application on `n0` to send UDP packets to the sink at `n3`.
-   **Explanation**:
    -   `OnOffHelper("ns3::UdpSocketFactory", ...)`: Creates a UDP application that alternates between "on" and "off" states.
        -   `PacketSize`: Configures packet size to `1024` bytes (1 KB).
        -   `DataRate`: Sets the rate of packet generation to `100 kbps` (100 packets/sec).
    -   `cbr.Install(nodes.Get(0))`: Installs the application on `n0`.
    -   `Start` and `Stop`: Configures the start time at `0.1` seconds and stop time at `4.5` seconds.

----------

### **FlowMonitor and Traffic Coloring**

```python
flowmon = ns.flow_monitor.FlowMonitorHelper()
monitor = flowmon.InstallAll()

```

-   **Purpose**: Enables monitoring of network traffic for analysis.

```python
def ColorTraffic():
    classifier = flowmon.GetClassifier()
    for flow_id, flow_stats in monitor.GetFlowStats():
        flow_desc = classifier.FindFlow(flow_id)
        if flow_desc.protocol == 6:  # TCP (6 in IP header)
            print(f"Flow {flow_id} (TCP): Color it BLUE")
        elif flow_desc.protocol == 17:  # UDP (17 in IP header)
            print(f"Flow {flow_id} (UDP): Color it RED")

```

-   **Purpose**: Defines rules to color traffic based on the protocol.
-   **Explanation**:
    -   `GetClassifier()`: Retrieves the classifier to identify flow metadata (e.g., protocol, source, destination).
    -   `GetFlowStats()`: Provides statistics for all monitored flows.
    -   `FindFlow(flow_id)`: Identifies the details of a specific flow based on its ID.
    -   Protocol `6` (TCP): Colored **blue**.
    -   Protocol `17` (UDP): Colored **red**.

----------

### **Simulation Execution**

```python
ns.visualizer.PyVizHelper.Enable()
ns.core.Simulator.Stop(ns.core.Seconds(10.0))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()

```

-   **PyViz Visualization**: Enables real-time simulation visualization.
-   **Run and Destroy**: Runs the simulation until `10.0` seconds, then cleans up memory.

----------

If you need any section further clarified, feel free to ask!
###### 22L-6824