terraform {
  required_providers {
    alteon = {
      source = "Radware/alteon"
    }
  }
}

resource "alteon_ssl_policy" "ssl_policy_outbound_be_ssl_inspection" {
  nameidindex = "Outbound_BE_SSL_Inspection"
  name = "Outbound Backend SSL Inspection"
  admin_status = 2
  convert = 3
  fessl = 3
  bessl = 2
  fe_tls11_version = 2
  be_tls11_version = 2
}

resource "alteon_ssl_policy" "ssl_policy_outbound_fe_ssl_inspection" {
  nameidindex = "Outbound_FE_SSL_Inspection"
  name = "Outbound Frontend SSL Inspection"
  admin_status = 2
  convert = 3
  fe_tls11_version = 2
  be_tls11_version = 2
}

resource "alteon_cli_command" "cli_slb_ssl_certs_group_242" {
  agalteonclicommand = "/c/slb/ssl/certs/group 242/type certificate/chainmod keyid/add \"1001\""
}

resource "alteon_cli_command" "cli_slb_ssl_certs_group_442" {
  agalteonclicommand = "/c/slb/ssl/certs/group 442/type certificate/chainmod keyid/add \"1001\""
}

resource "alteon_real_server" "real_server_101102" {
  index = "101102"
  ip_addr = "192.168.101.102"
  ip_ver = 1
  state = 2
}

resource "alteon_real_server" "real_server_101102_a" {
  index = "101102-a"
  ip_addr = "192.168.101.102"
  ip_ver = 1
  state = 2
}

resource "alteon_real_server" "real_server_101102_b" {
  index = "101102-b"
  ip_addr = "192.168.101.102"
  ip_ver = 1
  state = 2
}

resource "alteon_real_server" "real_server_101103" {
  index = "101103"
  ip_addr = "192.168.101.103"
  ip_ver = 1
  state = 2
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

resource "alteon_cli_command" "cli_slb_filt_1" {
  agalteonclicommand = "/c/slb/filt 1/dis/action redir/ipver v4/sip 10.12.25.13/smask 255.255.255.255/dip 10.12.148.220/dmask 255.255.255.255/proto tcp/dport https/group 1000/rport 8080/vlan any/applic http"
}

resource "alteon_cli_command" "cli_slb_filt_1_ssl" {
  agalteonclicommand = "/c/slb/filt 1/ssl/srvrcert cert 1001/sslpol system_pki_auth"
}

resource "alteon_cli_command" "cli_slb_filt_1_adv_redir" {
  agalteonclicommand = "/c/slb/filt 1/adv/redir/dbind forceproxy/rtproxy ena"
}

resource "alteon_virtual_server" "virtual_server_1000" {
  index = "1000"
  virt_server_ip_address = "10.2.0.213"
  virt_server_ip_ver = 1
  virt_server_state = 3
}

resource "alteon_virtual_service" "virtual_service_1000_443_https" {
  servindex = "1000"
  index = 1
  virt_port = 443
  real_port = 443
  real_group = "1"
  serv_cert = "1001"
  serv_cert_grp_mark = 0
}

resource "alteon_virtual_server" "virtual_server_1010" {
  index = "1010"
  virt_server_ip_address = "10.2.0.213"
  virt_server_ip_ver = 1
  virt_server_state = 3
}

resource "alteon_virtual_service" "virtual_service_1010_80_http" {
  servindex = "1010"
  index = 1
  virt_port = 80
  real_port = 80
  real_group = "1010"
}

resource "alteon_virtual_server" "virtual_server_1020" {
  index = "1020"
  virt_server_ip_address = "10.2.0.213"
  virt_server_ip_ver = 1
  virt_server_state = 3
}

resource "alteon_virtual_service" "virtual_service_1020_80_http" {
  servindex = "1020"
  index = 1
  virt_port = 80
  real_port = 80
  real_group = "1020"
}

resource "alteon_virtual_server" "virtual_server_1030" {
  index = "1030"
  virt_server_ip_address = "10.2.0.213"
  virt_server_ip_ver = 1
  virt_server_state = 3
}

resource "alteon_virtual_service" "virtual_service_1030_80_http" {
  servindex = "1030"
  index = 1
  virt_port = 80
  real_port = 80
  real_group = "1030"
}
