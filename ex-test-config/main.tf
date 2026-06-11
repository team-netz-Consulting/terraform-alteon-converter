resource "alteon_real_server" "real_server_101102" {
  index = "101102"
  elements {
    ipaddr = "192.168.101.102"
    ipver = 4
    state = 1
    name = "real_server_101102"
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

resource "alteon_real_server" "real_server_101103_xx" {
  index = "101103_xx"
  elements {
    ipaddr = "192.168.101.103"
    ipver = 4
    state = 1
  }
}