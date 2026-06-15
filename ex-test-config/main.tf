
resource "alteon_real_server" "real_server_101102" {
  index = "101102"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 1
    state = 2
  }
}

resource "alteon_real_server" "real_server_101102_a" {
  index = "101102-a"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 1
    state = 2
  }
}

resource "alteon_real_server" "real_server_101102_b" {
  index = "101102-b"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 1
    state = 2
  }
}

resource "alteon_real_server" "real_server_101103" {
  index = "101103"
  elements {
    ipaddr = "192.168.101.103"
    ipver = 1
    state = 2
  }
}

resource "alteon_server_group" "server_group_1000" {
  index = "1000"
  servers = ["101102"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_1010" {
  index = "1010"
  servers = ["101102-a"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_1020" {
  index = "1020"
  servers = ["101102-b"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_1030" {
  index = "1030"
  servers = ["101102-a", "101103"]
  name = "test_server_group_1030"
  metric = "roundrobin"
  health_check_layer = "icmp"
  ip_ver = 1
}

/*
resource "alteon_virtual_server" "virtual_server_1000" {
  index = "1000"
  elements {
    virtserveripaddress = "10.2.0.213"
    virtserveripver = 1
    virtserverstate = 3
    virtserverdname="virtual_server_1000"
  }
}
*/

resource "alteon_virtual_server" "TestVirtualServer1" {  
  index="Virt1-1"
  elements {
    	virtserveripaddress="10.10.10.10"
      virtserverstate=2
      //virtserverdname="virtual-Server-Domain-Update"
      //virtserverweight=data.alteon_virtual_server_data.VirtualServer-data.virtserverweight
      //virtservernat="14.24.4.5"
      //virtserverbwmcontract=1022
      //virtserveravail=2
      virtservervname="VirtualServerVName"
    }
  //depends_on = [alteon_server_group.LabServers]
}
/*
resource "alteon_virtual_service" "TestVirtualService" {  
  servindex="Virt1-1"
  index=1
  elements {
    	virtport=80
      realport=80
      dbind=2
      udpbalance=3
      pbind=3
      //cookiemode=3
    }
  depends_on = [alteon_virtual_server.TestVirtualServer1]
}

*/