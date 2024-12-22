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
