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