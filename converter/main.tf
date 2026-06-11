terraform {
  required_providers {
    alteon = {
      source = "Radware/alteon"
    }
  }
}

resource "alteon_cli_command" "cli_ssl_certs_group_242" {
  elements {
    agalteonclicommand = "/c/slb/ssl/certs/group 242/type certificate/chainmod keyid/add \"1001\""
  }
}

resource "alteon_cli_command" "cli_ssl_certs_group_442" {
  elements {
    agalteonclicommand = "/c/slb/ssl/certs/group 442/type certificate/chainmod keyid/add \"1001\""
  }
}

resource "alteon_real_server" "real_server_101102" {
  index = "101102"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 4
    state = 1
  }
}

resource "alteon_real_server" "real_server_101102_a" {
  index = "101102-a"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 4
    state = 1
  }
}

resource "alteon_real_server" "real_server_101102_b" {
  index = "101102-b"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 4
    state = 1
  }
}

resource "alteon_real_server" "real_server_101103" {
  index = "101103"
  elements {
    ipaddr = "192.168.101.103"
    ipver = 4
    state = 1
  }
}

resource "alteon_cli_command" "cli_group_1000" {
  elements {
    agalteonclicommand = "/c/slb/group 1000/ipver v4/add 101102"
  }
}

resource "alteon_cli_command" "cli_group_1010" {
  elements {
    agalteonclicommand = "/c/slb/group 1010/ipver v4/add 101102-a"
  }
}

resource "alteon_cli_command" "cli_group_1020" {
  elements {
    agalteonclicommand = "/c/slb/group 1020/ipver v4/add 101102-b"
  }
}

resource "alteon_cli_command" "cli_group_1030" {
  elements {
    agalteonclicommand = "/c/slb/group 1030/ipver v4/add 101102-a/add 101103"
  }
}

resource "alteon_virtual_server" "virtual_server_1000" {
  index = "1000"
  elements {
    virtserveripaddress = "10.2.0.213"
    virtserveripver = 4
    virtserverstate = 2
  }
}

resource "alteon_virtual_server" "virtual_server_1010" {
  index = "1010"
  elements {
    virtserveripaddress = "10.2.0.213"
    virtserveripver = 4
    virtserverstate = 2
  }
}

resource "alteon_virtual_server" "virtual_server_1020" {
  index = "1020"
  elements {
    virtserveripaddress = "10.2.0.213"
    virtserveripver = 4
    virtserverstate = 2
  }
}

resource "alteon_virtual_server" "virtual_server_1030" {
  index = "1030"
  elements {
    virtserveripaddress = "10.2.0.213"
    virtserveripver = 4
    virtserverstate = 2
  }
}

resource "alteon_virtual_service" "virtual_service_1000_443_https" {
  index     = 443
  servindex = "1000"
  elements {
    virtport = 443
    realport = 443
  }
  elements_2 {
    servcert = "1001"
  }
  elements_5 {
    servcertgrpmark = 0
  }
  elements_7 {
    realgroup = "1"
  }
}

resource "alteon_virtual_service" "virtual_service_1010_80_http" {
  index     = 80
  servindex = "1010"
  elements {
    virtport = 80
    realport = 80
  }
  elements_7 {
    realgroup = "1010"
  }
}

resource "alteon_virtual_service" "virtual_service_1020_80_http" {
  index     = 80
  servindex = "1020"
  elements {
    virtport = 80
    realport = 80
  }
  elements_7 {
    realgroup = "1020"
  }
}

resource "alteon_virtual_service" "virtual_service_1030_80_http" {
  index     = 80
  servindex = "1030"
  elements {
    virtport = 80
    realport = 80
  }
  elements_7 {
    realgroup = "1030"
  }
}
