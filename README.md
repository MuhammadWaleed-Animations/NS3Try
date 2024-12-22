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

# Add TCP agent on n1 and sink on n3
tcp_source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
tcp_source.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data
tcp_app = tcp_source.Install(nodes.Get(1))
tcp_app.Start(ns.core.Seconds(0.5))  # Start at 0.5 seconds
tcp_app.Stop(ns.core.Seconds(4.0))  # Stop at 4.0 seconds

tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
tcp_sink_app = tcp_sink.Install(nodes.Get(3))
tcp_sink_app.Start(ns.core.Seconds(0.0))  # Start at simulation time 0
tcp_sink_app.Stop(ns.core.Seconds(10.0))

# Add UDP agent on n0 and null agent on n3
udp_source = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
udp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
udp_source.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # Rate: 100 packets/sec
udp_app = udp_source.Install(nodes.Get(0))
udp_app.Start(ns.core.Seconds(0.1))  # Start at 0.1 seconds
udp_app.Stop(ns.core.Seconds(4.5))  # Stop at 4.5 seconds

udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
udp_sink_app = udp_sink.Install(nodes.Get(3))
udp_sink_app.Start(ns.core.Seconds(0.0))
udp_sink_app.Stop(ns.core.Seconds(10.0))

# Enable FlowMonitor to track and color traffic
flowmon = ns.flow_monitor.FlowMonitorHelper()
monitor = flowmon.InstallAll()

# Run simulation
ns.core.Simulator.Stop(ns.core.Seconds(10.0))

# Define Coloring Rules
def ColorTraffic():
    classifier = flowmon.GetClassifier()
    for flow_id, flow_stats in monitor.GetFlowStats():
        flow_desc = classifier.FindFlow(flow_id)
        if flow_desc.protocol == 6:  # TCP (6 in IP header)
            print(f"Flow {flow_id} (TCP): Color it BLUE")
        elif flow_desc.protocol == 17:  # UDP (17 in IP header)
            print(f"Flow {flow_id} (UDP): Color it RED")

# Enable PyViz and add Coloring Callback
ns.visualizer.PyVizHelper.Enable()
ColorTraffic()

# Run and destroy
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()

```

  
----------

### **Import Required Modules**

```python
import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.visualizer

```

-   **Purpose**: These modules provide the building blocks to set up, configure, and simulate a network in NS-3.
    -   `ns.applications`: Contains applications like TCP, UDP, FTP, and CBR that simulate traffic generation.
    -   `ns.core`: Provides the core functionality like events, timers, and simulation controls.
    -   `ns.internet`: Offers tools for IP-based networking (IPv4, routing, etc.).
    -   `ns.network`: Manages network nodes, channels, and data links.
    -   `ns.point_to_point`: Includes point-to-point link helpers for direct connections.
    -   `ns.visualizer`: Enables PyViz for visualization of network simulations.

----------

### **Node Creation**

```python
nodes = ns.network.NodeContainer()
nodes.Create(4)  # Create 4 nodes: n0, n1, n2, n3

```

-   `ns.network.NodeContainer`: A container to manage a group of nodes.
-   `nodes.Create(4)`: Creates 4 nodes in the container, named `n0`, `n1`, `n2`, and `n3`.

**Variations**:

-   `nodes.Add(node)`: Add an existing node to the container.
-   Use `NodeContainer()` to group specific nodes together if the network is complex.

----------

### **Installing Internet Stack**

```python
stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

```

-   `ns.internet.InternetStackHelper`: Helps to install networking protocols like IPv4, IPv6, and routing on the nodes.
-   `stack.Install(nodes)`: Installs the internet stack on all nodes.

**Variations**:

-   Install on specific nodes: `stack.Install(nodes.Get(0))`.

----------

### **Point-to-Point Links**

Each duplex link is configured with specific bandwidth, delay, and queue size.

#### **Link Between n0 and n2**

```python
p2p_n0_n2 = ns.point_to_point.PointToPointHelper()
p2p_n0_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
p2p_n0_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
p2p_n0_n2.SetQueue("ns3::DropTailQueue", "MaxSize", ns.core.StringValue("10p"))
devices_n0_n2 = p2p_n0_n2.Install(nodes.Get(0), nodes.Get(2))

```

-   `ns.point_to_point.PointToPointHelper`: A helper for creating point-to-point links.
-   `SetDeviceAttribute`: Sets attributes for devices on the link.
    -   `"DataRate"`: Defines link bandwidth as 2 Mbps.
-   `SetChannelAttribute`: Sets attributes for the link channel.
    -   `"Delay"`: Defines the propagation delay as 10 ms.
-   `SetQueue`: Specifies the queue type (`DropTailQueue`) and maximum queue size (10 packets, `"10p"`).
-   `Install(nodes.Get(0), nodes.Get(2))`: Creates a duplex link between `n0` and `n2`.

**Variations**:

-   Use `SetQueue` to configure other queue types (e.g., `ns3::RedQueue`).

----------

#### **Links Between n1-n2 and n2-n3**

Similar configurations are applied for other links with specific bandwidths and delays:

```python
p2p_n1_n2 = ns.point_to_point.PointToPointHelper()
p2p_n1_n2.SetDeviceAttribute("DataRate", ns.core.StringValue("2Mbps"))
p2p_n1_n2.SetChannelAttribute("Delay", ns.core.StringValue("10ms"))
p2p_n1_n2.SetQueue("ns3::DropTailQueue", "MaxSize", ns.core.StringValue("10p"))
devices_n1_n2 = p2p_n1_n2.Install(nodes.Get(1), nodes.Get(2))

p2p_n2_n3 = ns.point_to_point.PointToPointHelper()
p2p_n2_n3.SetDeviceAttribute("DataRate", ns.core.StringValue("1.7Mbps"))
p2p_n2_n3.SetChannelAttribute("Delay", ns.core.StringValue("20ms"))
p2p_n2_n3.SetQueue("ns3::DropTailQueue", "MaxSize", ns.core.StringValue("10p"))
devices_n2_n3 = p2p_n2_n3.Install(nodes.Get(2), nodes.Get(3))

```

----------

### **Assigning IP Addresses**

```python
address = ns.internet.Ipv4AddressHelper()

# Assign IP to n0-n2 link
address.SetBase(ns.network.Ipv4Address("10.1.1.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n0_n2 = address.Assign(devices_n0_n2)

# Assign IP to n1-n2 link
address.SetBase(ns.network.Ipv4Address("10.1.2.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n1_n2 = address.Assign(devices_n1_n2)

# Assign IP to n2-n3 link
address.SetBase(ns.network.Ipv4Address("10.1.3.0"), ns.network.Ipv4Mask("255.255.255.0"))
interfaces_n2_n3 = address.Assign(devices_n2_n3)

```

-   `Ipv4AddressHelper`: Automates IP assignment for links.
-   `SetBase`: Sets the base address and subnet mask for each link.
-   `Assign`: Allocates IPs to devices on the link.

**Variations**:

-   Use `SetBase` with different subnets for larger networks.

----------

### **Routing Setup**

```python
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

```

-   `Ipv4GlobalRoutingHelper.PopulateRoutingTables`: Automatically sets up routing tables for all nodes.

----------

### **Application Setup**

#### **TCP**

```python
tcp_source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
tcp_source.SetAttribute("MaxBytes", ns.core.UintegerValue(0))
tcp_app = tcp_source.Install(nodes.Get(1))
tcp_app.Start(ns.core.Seconds(0.5))
tcp_app.Stop(ns.core.Seconds(4.0))

```

-   **`BulkSendHelper`**: Sends bulk data over a TCP connection.
    -   `"MaxBytes"`: 0 for unlimited data.
    -   Destination: `interfaces_n2_n3.GetAddress(1)` (IP of `n3`).
-   **Start/Stop**: Activates between 0.5 and 4.0 seconds.

#### **UDP**

```python
udp_source = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
udp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))
udp_source.SetAttribute("DataRate", ns.core.StringValue("100kbps"))
udp_app = udp_source.Install(nodes.Get(0))
udp_app.Start(ns.core.Seconds(0.1))
udp_app.Stop(ns.core.Seconds(4.5))

```

-   **`OnOffHelper`**: Generates traffic with bursts (on/off periods).
    -   `"PacketSize"`: 1 KB packets.
    -   `"DataRate"`: 100 packets/sec.

----------


### **Visualization**

#### **1. Enable FlowMonitor**

```python
flowmon = ns.flow_monitor.FlowMonitorHelper()
monitor = flowmon.InstallAll()

```

-   **`ns.flow_monitor.FlowMonitorHelper()`**:
    
    -   A helper class in NS3 that simplifies the setup of the **FlowMonitor** system. The FlowMonitor collects traffic flow statistics during the simulation, such as packet counts, delays, and throughput.
-   **`monitor = flowmon.InstallAll()`**:
    
    -   This installs the **FlowMonitor** on all nodes in the simulation. It ensures that traffic on all links is tracked.

----------

#### **2. Run Simulation**

```python
ns.core.Simulator.Stop(ns.core.Seconds(10.0))

```

-   The simulator is configured to run for 10 seconds, after which it automatically stops. This ensures that all traffic flows within this duration are captured.

----------

#### **3. Define Coloring Rules**

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

-   **Purpose**:
    
    -   This function applies the traffic coloring rules based on the **protocol** used by each flow. Flows are identified using their `flow_id`, and the corresponding protocol is checked to determine its color.
-   **Step-by-Step Breakdown**:
    
    1.  **`classifier = flowmon.GetClassifier()`**:
        
        -   Retrieves the classifier object. It maps flow IDs to flow descriptors (source/destination IPs, ports, and protocol).
    2.  **`monitor.GetFlowStats()`**:
        
        -   Obtains the statistics for each flow (e.g., bytes sent/received, delays).
    3.  **`classifier.FindFlow(flow_id)`**:
        
        -   Retrieves the **flow descriptor** for the given `flow_id`. This descriptor contains key details about the flow:
            -   `sourceAddress`: Source IP address.
            -   `destinationAddress`: Destination IP address.
            -   `protocol`: The protocol in use (6 for TCP, 17 for UDP).
    4.  **Protocol Checks**:
        
        -   **`flow_desc.protocol == 6`**:
            -   If the protocol is **6** (TCP, as per the IP header), the flow is colored **BLUE**.
        -   **`flow_desc.protocol == 17`**:
            -   If the protocol is **17** (UDP, as per the IP header), the flow is colored **RED**.
    5.  **Output**:
        
        -   Prints the flow ID, protocol, and assigned color.

----------

#### **4. Enable PyViz and Add Coloring Callback**

```python
ns.visualizer.PyVizHelper.Enable()
ColorTraffic()

```

-   **`ns.visualizer.PyVizHelper.Enable()`**:
    
    -   Enables **PyViz**, a visualization tool that provides a real-time view of the network simulation. It allows you to observe the simulation topology and packet flows interactively.
-   **`ColorTraffic()`**:
    
    -   This function is called to apply the coloring rules defined earlier. It processes the flows and prints their assigned colors based on their protocols.

----------

### **Explanation of Flow Coloring**

-   **Why is Flow Coloring Important?**
    
    -   It helps differentiate traffic types visually, making it easier to analyze network performance for different protocols.
-   **Key Mechanisms**:
    
    -   **FlowMonitor**: Tracks and logs all flows during the simulation.
    -   **Classifier**: Maps flow IDs to protocol and other metadata.
    -   **Color Assignment**:
        -   **TCP** → **Blue** (e.g., Bulk data transfer).
        -   **UDP** → **Red** (e.g., Real-time video or VoIP).

----------

### **Improvements**

-   **Dynamic Visualization**:
    -   The current code prints flow coloring information to the console. For dynamic visualization, you could integrate coloring directly into **PyViz** if supported.
-   **Real-Time Monitoring**:
    -   Update flow statistics and apply coloring rules dynamically during the simulation, instead of after it ends.

----------

### **Run the Simulation**

```python
ns.core.Simulator.Stop(ns.core.Seconds(10.0))
ns.core.Simulator.Run()
ns.core.Simulator.Destroy()

```

-   `Stop`: Stops the simulation after 10 seconds.
-   `Run`: Executes the simulation.
-   `Destroy`: Cleans up resources.

----------

# More Details:


```python

# Enable routing
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

# Add TCP agent on n1 and sink on n3
tcp_source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
tcp_source.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data
tcp_app = tcp_source.Install(nodes.Get(1))
tcp_app.Start(ns.core.Seconds(0.5))  # Start at 0.5 seconds
tcp_app.Stop(ns.core.Seconds(4.0))  # Stop at 4.0 seconds

tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
tcp_sink_app = tcp_sink.Install(nodes.Get(3))
tcp_sink_app.Start(ns.core.Seconds(0.0))  # Start at simulation time 0
tcp_sink_app.Stop(ns.core.Seconds(10.0))

# Add UDP agent on n0 and null agent on n3
udp_source = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
udp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
udp_source.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # Rate: 100 packets/sec
udp_app = udp_source.Install(nodes.Get(0))
udp_app.Start(ns.core.Seconds(0.1))  # Start at 0.1 seconds
udp_app.Stop(ns.core.Seconds(4.5))  # Stop at 4.5 seconds

udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
udp_sink_app = udp_sink.Install(nodes.Get(3))
udp_sink_app.Start(ns.core.Seconds(0.0))
udp_sink_app.Stop(ns.core.Seconds(10.0))

# Visualization of flows
ns.visualizer.PyVizHelper.Enable()

```

### TCP and UDP detail

The provided block of code configures the traffic sources and sinks for both TCP and UDP flows, and then enables network visualization. Let's break it down thoroughly to understand the purpose, functionality, and any variations possible for each line.



### **Enabling Global Routing**

```python
ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables()

```

-   **Purpose**: Automatically sets up routing tables for the nodes in the network.
    -   **Global Routing**: Each node calculates its routing table based on the shortest paths to every other node in the network.
-   **How it works**:
    -   Uses Dijkstra's algorithm to compute the routes.
    -   Adds entries to the `Ipv4RoutingTable` for each node.
-   **Alternative**: For custom routes, you can use `StaticRoutingHelper` to manually define routes instead of using `Ipv4GlobalRoutingHelper`.

----------

### **Configuring the TCP Flow**

#### **Setting Up the TCP Source on `n1`**

```python
tcp_source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 9))
tcp_source.SetAttribute("MaxBytes", ns.core.UintegerValue(0))  # Unlimited data

```

1.  **`ns.applications.BulkSendHelper`**:
    -   Used to create a TCP source that sends data in bulk to a specified destination.
    -   `"ns3::TcpSocketFactory"`: Specifies that the transport protocol is TCP.
    -   `ns.network.InetSocketAddress`: Defines the destination address and port:
        -   `interfaces_n2_n3.GetAddress(1)`: IP address of the receiver node (`n3`).
        -   `9`: Destination port number.
2.  **Setting Attributes**:
    -   `"MaxBytes"`: Limits the amount of data sent by the TCP source.
        -   Here, `0` means unlimited data will be sent.

#### **Installing the TCP Application on `n1`**

```python
tcp_app = tcp_source.Install(nodes.Get(1))
tcp_app.Start(ns.core.Seconds(0.5))  # Start at 0.5 seconds
tcp_app.Stop(ns.core.Seconds(4.0))  # Stop at 4.0 seconds

```

1.  **`Install(nodes.Get(1))`**:
    -   Installs the configured TCP source application on node `n1`.
2.  **`Start` and `Stop`**:
    -   Configures when the application starts and stops.
    -   Start at `0.5` seconds into the simulation.
    -   Stop at `4.0` seconds.

----------

#### **Setting Up the TCP Sink on `n3`**

```python
tcp_sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 9))
tcp_sink_app = tcp_sink.Install(nodes.Get(3))
tcp_sink_app.Start(ns.core.Seconds(0.0))  # Start at simulation time 0
tcp_sink_app.Stop(ns.core.Seconds(10.0))

```

1.  **`ns.applications.PacketSinkHelper`**:
    -   Used to create a sink application that receives packets sent to it.
    -   `"ns3::TcpSocketFactory"`: Indicates the sink is for TCP traffic.
    -   `ns.network.InetSocketAddress`:
        -   `ns.network.Ipv4Address.GetAny()`: Allows the sink to receive packets from any source.
        -   `9`: The port on which the sink listens for packets.
2.  **Installing the Application**:
    -   `tcp_sink.Install(nodes.Get(3))`: Installs the TCP sink on node `n3`.
    -   Start time (`0.0` seconds): The sink starts receiving packets immediately when the simulation begins.
    -   Stop time (`10.0` seconds): The sink continues to listen until the end of the simulation.

----------

### **Configuring the UDP Flow**

#### **Setting Up the UDP Source on `n0`**

```python
udp_source = ns.applications.OnOffHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(interfaces_n2_n3.GetAddress(1), 10))
udp_source.SetAttribute("PacketSize", ns.core.UintegerValue(1024))  # 1 KB packets
udp_source.SetAttribute("DataRate", ns.core.StringValue("100kbps"))  # Rate: 100 packets/sec

```

1.  **`ns.applications.OnOffHelper`**:
    -   Generates traffic in bursts, switching between "on" and "off" states.
    -   `"ns3::UdpSocketFactory"`: Specifies that the transport protocol is UDP.
    -   Destination Address: `interfaces_n2_n3.GetAddress(1)` refers to the IP of `n3`.
    -   Destination Port: `10`.
2.  **Setting Attributes**:
    -   `"PacketSize"`: Size of each UDP packet in bytes (1024 bytes = 1 KB).
    -   `"DataRate"`: Specifies the sending rate for packets (100 kbps = 100 packets/sec).

#### **Installing the UDP Application on `n0`**

```python
udp_app = udp_source.Install(nodes.Get(0))
udp_app.Start(ns.core.Seconds(0.1))  # Start at 0.1 seconds
udp_app.Stop(ns.core.Seconds(4.5))  # Stop at 4.5 seconds

```

1.  **`Install(nodes.Get(0))`**:
    -   Installs the configured UDP source application on node `n0`.
2.  **`Start` and `Stop`**:
    -   The application starts at `0.1` seconds.
    -   Stops at `4.5` seconds.

----------

#### **Setting Up the UDP Sink on `n3`**

```python
udp_sink = ns.applications.PacketSinkHelper("ns3::UdpSocketFactory", ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), 10))
udp_sink_app = udp_sink.Install(nodes.Get(3))
udp_sink_app.Start(ns.core.Seconds(0.0))
udp_sink_app.Stop(ns.core.Seconds(10.0))

```

1.  **`ns.applications.PacketSinkHelper`**:
    -   Configures a sink for UDP traffic.
    -   `"ns3::UdpSocketFactory"`: Indicates the sink is for UDP traffic.
    -   `ns.network.InetSocketAddress`:
        -   `ns.network.Ipv4Address.GetAny()`: Allows the sink to receive packets from any source.
        -   `10`: The port on which the sink listens for UDP packets.
2.  **Installing the Application**:
    -   `udp_sink.Install(nodes.Get(3))`: Installs the UDP sink on node `n3`.
    -   The sink starts immediately (`0.0` seconds) and listens until the simulation ends (`10.0` seconds).

----------

### **Enabling Visualization**

```python
ns.visualizer.PyVizHelper.Enable()

```

1.  **`PyVizHelper.Enable()`**:
    -   Launches the PyViz GUI to visualize the network topology and real-time traffic flows during the simulation.
    -   You can observe packets traversing the links and verify traffic behaviors.

----------

### **Summary of Traffic Flows**

-   **TCP Flow**:
    -   Source: `n1` (starts at 0.5 seconds, stops at 4.0 seconds).
    -   Sink: `n3` (listens on port 9).
-   **UDP Flow**:
    -   Source: `n0` (starts at 0.1 seconds, stops at 4.5 seconds).
    -   Sink: `n3` (listens on port 10).

The setup achieves distinct traffic flows, with different transport protocols and parameters, and uses PyViz for network visualization.

###### 22L-6824