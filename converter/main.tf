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
}

resource "alteon_ssl_policy" "ssl_policy_outbound_fe_ssl_inspection" {
  nameidindex = "Outbound_FE_SSL_Inspection"
  name = "Outbound Frontend SSL Inspection"
  admin_status = 2
  convert = 3
}

resource "alteon_ssl_policy" "ssl_policy_comca44" {
  nameidindex = "comca44"
  admin_status = 2
  convert = 3
  cipher_userdef = "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256"
  intermca_chain_type = "group"
  intermca_chain_name = "11"
  secreneg = "0"
  bessl = 2
  pass_info_frontend = 2
}

resource "alteon_vrrp" "vrrp_123" {
  index = 123
  vrid = 123
  version = "v4"
  addr = "1.2.3.50"
  if_index = 4
  priority = 22
  state = false
  preempt = false
  sharing = false
  track_ip_intf = true
}

resource "alteon_vrrp" "vrrp_124" {
  index = 124
  vrid = 124
  version = "v4"
  addr = "1.2.3.51"
  if_index = 4
  priority = 101
  state = true
  preempt = false
  sharing = false
  track_ip_intf = true
}

resource "alteon_vrrp" "vrrp_138" {
  index = 138
  vrid = 138
  version = "v4"
  addr = "1.2.3.30"
  if_index = 4
  priority = 101
  state = false
  sharing = false
  track_ip_intf = true
}

resource "alteon_vrrp" "vrrp_141" {
  index = 141
  vrid = 141
  version = "v4"
  addr = "1.2.3.38"
  if_index = 4
  priority = 222
  state = true
  preempt = false
  sharing = false
  track_ip_intf = true
}

resource "alteon_vrrp" "vrrp_142" {
  index = 142
  vrid = 142
  version = "v4"
  addr = "1.2.3.39"
  if_index = 4
  priority = 222
  state = true
  preempt = false
  sharing = false
  track_ip_intf = true
}

resource "alteon_cli_command" "cli_slb_ssl_certs_group_1" {
  agalteonclicommand = "/c/slb/ssl/certs/group 1/type intermca/add \"4\"/add \"3\""
}

resource "alteon_cli_command" "cli_slb_ssl_certs_group_11" {
  agalteonclicommand = "/c/slb/ssl/certs/group 11/type intermca/add \"14\"/add \"13\""
}

resource "alteon_cli_command" "cli_slb_ssl_certs_group_ergebniswweb" {
  agalteonclicommand = "/c/slb/ssl/certs/group ergebniswweb/type certificate/add \"web.intern.example.de\""
}

resource "alteon_cli_command" "cli_slb_advhc_health_ergebnisw_50001_http" {
  agalteonclicommand = "/c/slb/advhc/health ergebnisw_50001 HTTP/dport 50001/ssl enabled"
}

resource "alteon_cli_command" "cli_slb_advhc_health_ergebnisw_50001_http_http" {
  agalteonclicommand = "/c/slb/advhc/health ergebnisw_50001 HTTP/http/path \"/ergebnisw\"/response 200,301,302,307 none \"\""
}

resource "alteon_real_server" "real_server_15" {
  index = "15"
  ip_addr = "1.2.3.31"
  ip_ver = 1
  name = "testappp01_443"
  state = 2
}

resource "alteon_real_server" "real_server_16" {
  index = "16"
  ip_addr = "1.2.3.32"
  ip_ver = 1
  name = "testappp02_443"
  state = 2
}

resource "alteon_real_server" "real_server_41" {
  index = "41"
  ip_addr = "1.2.3.31"
  ip_ver = 1
  name = "testappp01_50001"
  state = 2
}

resource "alteon_real_server" "real_server_42" {
  index = "42"
  ip_addr = "1.2.3.32"
  ip_ver = 1
  name = "testappp02_50001"
  state = 2
}

resource "alteon_real_server" "real_server_43" {
  index = "43"
  ip_addr = "1.2.3.33"
  ip_ver = 1
  name = "testappp03_50001"
  state = 2
}

resource "alteon_real_server" "real_server_44" {
  index = "44"
  ip_addr = "1.2.3.34"
  ip_ver = 1
  name = "testappp04_50001"
  state = 2
}

resource "alteon_real_server" "real_server_102" {
  index = "102"
  ip_addr = "1.2.3.11"
  ip_ver = 1
  name = "testapp201_443"
  state = 2
}

resource "alteon_real_server" "real_server_103" {
  index = "103"
  ip_addr = "1.2.3.12"
  ip_ver = 1
  name = "testapp202_443"
  state = 2
}

resource "alteon_real_server" "real_server_141" {
  index = "141"
  ip_addr = "1.2.3.31"
  ip_ver = 1
  name = "testappp01_51001"
  state = 2
}

resource "alteon_real_server" "real_server_142" {
  index = "142"
  ip_addr = "1.2.3.32"
  ip_ver = 1
  name = "testappp02_51001"
  state = 2
}

resource "alteon_real_server" "real_server_143" {
  index = "143"
  ip_addr = "1.2.3.33"
  ip_ver = 1
  name = "testappp03_51001"
  state = 2
}

resource "alteon_real_server" "real_server_144" {
  index = "144"
  ip_addr = "1.2.3.34"
  ip_ver = 1
  name = "testappp04_51001"
  state = 2
}

resource "alteon_real_server" "real_server_605" {
  index = "605"
  ip_addr = "1.2.3.11"
  ip_ver = 1
  name = "testapp201_50001"
  state = 2
}

resource "alteon_real_server" "real_server_607" {
  index = "607"
  ip_addr = "1.2.3.12"
  ip_ver = 1
  name = "testapp202_50001"
  state = 2
}

resource "alteon_real_server" "real_server_615" {
  index = "615"
  ip_addr = "1.2.3.11"
  ip_ver = 1
  name = "testapp201_51001"
  state = 2
}

resource "alteon_real_server" "real_server_617" {
  index = "617"
  ip_addr = "1.2.3.12"
  ip_ver = 1
  name = "testapp202_51001"
  state = 2
}

resource "alteon_real_server" "real_server_18812" {
  index = "18812"
  ip_addr = "1.2.3.12"
  ip_ver = 1
  state = 2
}

resource "alteon_real_server" "real_server_18813" {
  index = "18813"
  ip_addr = "1.2.3.13"
  ip_ver = 1
  state = 2
}

resource "alteon_real_server" "real_server_test_50001" {
  index = "test_50001"
  ip_addr = "1.2.3.11"
  ip_ver = 1
  name = "testapp201 port 50001"
  state = 2
  health_id = "ergebnisw_50001"
}

resource "alteon_real_server" "real_server_test_51001" {
  index = "test_51001"
  ip_addr = "1.2.3.11"
  ip_ver = 1
  name = "testapp201 port 51001"
  state = 2
}

resource "alteon_server_group" "server_group_12" {
  index = "12"
  servers = ["15", "16"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_13" {
  index = "13"
  servers = ["18812", "18813"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_22" {
  index = "22"
  servers = ["41", "42", "43", "44", "141", "142", "143", "144", "test_50001", "test_51001"]
  metric = "roundrobin"
  ip_ver = 1
}

resource "alteon_server_group" "server_group_33" {
  index = "33"
  servers = ["test_50001", "test_51001"]
  metric = "roundrobin"
  ip_ver = 1
}

resource "alteon_server_group" "server_group_100" {
  index = "100"
  servers = ["102", "103"]
  ip_ver = 1
}

resource "alteon_server_group" "server_group_500" {
  index = "500"
  ip_ver = 1
}

resource "alteon_cli_command" "cli_slb_real_41_layer7" {
  agalteonclicommand = "/c/slb/real 41/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_42_layer7" {
  agalteonclicommand = "/c/slb/real 42/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_43_layer7" {
  agalteonclicommand = "/c/slb/real 43/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_44_layer7" {
  agalteonclicommand = "/c/slb/real 44/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_141_layer7" {
  agalteonclicommand = "/c/slb/real 141/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_142_layer7" {
  agalteonclicommand = "/c/slb/real 142/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_143_layer7" {
  agalteonclicommand = "/c/slb/real 143/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_144_layer7" {
  agalteonclicommand = "/c/slb/real 144/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_605_layer7" {
  agalteonclicommand = "/c/slb/real 605/layer7/exclude e/addlb 3"
}

resource "alteon_cli_command" "cli_slb_real_607_layer7" {
  agalteonclicommand = "/c/slb/real 607/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_615_layer7" {
  agalteonclicommand = "/c/slb/real 615/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_617_layer7" {
  agalteonclicommand = "/c/slb/real 617/layer7/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_test_50001_layer7" {
  agalteonclicommand = "/c/slb/real test_50001/layer7/exclude e/addlb 2"
}

resource "alteon_cli_command" "cli_slb_real_test_51001_layer7" {
  agalteonclicommand = "/c/slb/real test_51001/layer7/addlb 2"
}

resource "alteon_virtual_server" "virtual_server_1" {
  index = "1"
  virt_server_ip_address = "1.2.3.38"
  virt_server_ip_ver = 1
  virt_server_state = 2
}

resource "alteon_virtual_service" "virtual_service_1_443_https" {
  servindex = "1"
  index = 1
  virt_port = 443
  real_port = 443
  real_group = "100"
}

resource "alteon_virtual_server" "virtual_server_11" {
  index = "11"
  virt_server_ip_address = "1.2.3.39"
  virt_server_ip_ver = 1
  virt_server_state = 2
}

resource "alteon_virtual_service" "virtual_service_11_22_ssh" {
  servindex = "11"
  index = 1
  virt_port = 22
  real_port = 22
  real_group = "13"
}

resource "alteon_virtual_server" "virtual_server_21" {
  index = "21"
  virt_server_ip_address = "1.2.3.50"
  virt_server_ip_ver = 1
  virt_server_state = 3
}

resource "alteon_virtual_service" "virtual_service_21_443_https" {
  servindex = "21"
  index = 1
  virt_port = 443
  real_port = 0
  real_group = "22"
  time_out = 30
  d_bind = 2
  x_forwarded_for = 2
  ss_lpol = "comca44"
  serv_cert = "ergebniswweb"
  serv_cert_grp_mark = 1
}

resource "alteon_virtual_service" "virtual_service_21_80_http" {
  servindex = "21"
  index = 2
  virt_port = 80
  real_port = 80
  real_group = "1"
  d_bind = 2
  action = 2
  redirect = "https://$HOST/$PATH?$QUERY"
}

resource "alteon_virtual_server" "virtual_server_22" {
  index = "22"
  virt_server_ip_address = "1.2.3.51"
  virt_server_ip_ver = 1
  virt_server_state = 2
}

resource "alteon_virtual_service" "virtual_service_22_443_https" {
  servindex = "22"
  index = 1
  virt_port = 443
  real_port = 0
  real_group = "33"
  time_out = 2
  d_bind = 2
  x_forwarded_for = 2
  ss_lpol = "comca44"
  serv_cert = "ergebniswweb"
  serv_cert_grp_mark = 1
}

resource "alteon_virtual_service" "virtual_service_22_80_http" {
  servindex = "22"
  index = 2
  virt_port = 80
  real_port = 80
  real_group = "1"
  d_bind = 2
  action = 2
  redirect = "https://$HOST/$PATH?$QUERY"
}
