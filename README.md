# Alteon Configuration to Terraform Converter

Convert Radware Alteon configuration dumps into Terraform resources using the Radware Alteon Terraform Provider.

## Overview

This tool parses Radware Alteon configuration dumps and generates Terraform resources that can be used to manage existing Alteon load balancer configurations through Terraform.

The converter focuses on Server Load Balancing (SLB), SSL, and High Availability (HA) objects and generates native Terraform resources whenever supported by the provider.

Unsupported or currently unmapped objects are exported as `alteon_cli_command` resources.

The generated Terraform code is intended as a migration and onboarding tool for existing Alteon environments.

---

## Features

### Native Terraform Resources

The converter currently supports:

| Alteon Configuration        | Terraform Resource                                  |
| --------------------------- | --------------------------------------------------- |
| `/c/slb/real`               | `alteon_real_server`                                |
| `/c/slb/group`              | `alteon_server_group`                               |
| `/c/slb/virt`               | `alteon_virtual_server`                             |
| `/c/slb/virt/service`       | `alteon_virtual_service`                            |
| `/c/slb/ssl/sslpol`         | `alteon_ssl_policy`                                 |
| `/c/slb/ssl/certs/cert`     | `alteon_ssl_cert`                                   |
| `/c/slb/ssl/certs/intermca` | `alteon_ssl_cert`                                   |
| `/c/slb/ssl/certs/group`    | `alteon_ssl_cert_group`                             |
| `/c/slb/http2/*`            | `alteon_http2_policy`                               |
| `/c/slb/advhc/health`       | `alteon_advhc_*`                                    |
| `/c/slb/filt`               | `alteon_filter`                                     |
| `/c/slb/pip`                | `alteon_pip`                                        |
| `/c/slb/dataclass`          | `alteon_data_class`                                 |
| `/c/slb/contentclass`       | `alteon_content_class`                              |
| `/c/slb/appshape`           | `alteon_appshape_script`, `alteon_appshape_binding` |
| `/c/l3/vrrp/vr`             | `alteon_vrrp`                                       |
| `/c/l3/vrrp/vrgroup`        | `alteon_vrrp_group`                                 |

---

### CLI Fallback Resources

The following objects are currently exported as `alteon_cli_command` resources:

| Alteon Configuration       |
| -------------------------- |
| certificate/key/request payload imports |
| unsupported AdvHC types    |
| unsupported Alteon objects |

---

## Import Generation

The converter automatically generates Terraform import blocks for:

* Real Servers
* Server Groups
* Virtual Servers
* Virtual Services
* Filters
* Advanced Health Checks
* PIP entries
* Data Classes
* Content Classes
* AppShape Scripts
* AppShape Bindings
* SSL Policies
* SSL Certificates
* SSL Certificate Groups
* HTTP/2 Policies
* VRRP Instances
* VRRP Groups

Example:

```hcl
import {
  to = alteon_virtual_server.virtual_server_21
  id = "21"
}

import {
  to = alteon_virtual_service.virtual_service_21_443_https
  id = "21/1"
}

import {
  to = alteon_vrrp.vrrp_124
  id = "124"
}

import {
  to = alteon_vrrp_group.vrrp_group_1
  id = "1"
}

import {
  to = alteon_filter.filter_1
  id = "1"
}

import {
  to = alteon_advhc_http.advhc_http_checkout
  id = "checkout"
}

import {
  to = alteon_ssl_cert.ssl_cert_web_3
  id = "web/3"
}

import {
  to = alteon_ssl_cert_group.ssl_cert_group_public
  id = "public"
}
```

Filter enum fields are emitted as provider numeric values. For example,
`action redirect` becomes `action = 3` and `nat source-address` becomes `nat = 2`.

---

## Virtual Service Handling

The Alteon provider uses a different service key model than the Alteon CLI.

### Alteon

```text
/c/slb/virt 21/service 443 https
```

### Terraform

```hcl
resource "alteon_virtual_service" "virtual_service_21_443_https" {
  servindex = "21"
  index     = 1

  virt_port = 443
  real_port = 443
}
```

Where:

| Field       | Meaning                                       |
| ----------- | --------------------------------------------- |
| `servindex` | Virtual Server ID                             |
| `index`     | Service sequence number on the Virtual Server |
| `virt_port` | Listener Port                                 |
| `real_port` | Backend Port                                  |

Import format:

```hcl
id = "21/1"
```

---

## VRRP Support

### Virtual Router

Example:

```text
/c/l3/vrrp/vr 124
    ena
    ipver v4
    vrid 124
    if 4
    prio 101
    addr 1.2.3.51
```

Generated:

```hcl
resource "alteon_vrrp" "vrrp_124" {
  index    = 124
  vrid     = 124

  addr     = "1.2.3.51"

  if_index = 4
  priority = 101

  state    = true
  version  = "v4"
}
```

---

### VRRP Group

Example:

```text
/c/l3/vrrp/vrgroup 1
    prio 101
    add 251
    add 248
```

Generated:

```hcl
resource "alteon_vrrp_group" "vrrp_group_1" {
  index = 1
  vrid  = 1

  priority = 101

  virtual_routers = [
    251,
    248
  ]
}
```

The converter automatically aggregates all:

```text
add <vr-id>
```

entries into:

```hcl
virtual_routers = [...]
```

---

## Server Group Support

Supported attributes:

* servers
* name
* metric
* health_check_layer
* health_id
* backup_server
* backup_group
* real_threshold
* slowstart
* ip_ver

Example:

```text
/c/slb/group 1030
    ipver v4
    metric roundrobin
    health icmp
    add 101102
    add 101103
```

becomes:

```hcl
resource "alteon_server_group" "server_group_1030" {
  index = "1030"

  servers = [
    "101102",
    "101103"
  ]

  metric             = "roundrobin"
  health_check_layer = "icmp"
  ip_ver             = 1
}
```

---

## Output Structure

Virtual Services are automatically grouped below their Virtual Server:

```hcl
resource "alteon_virtual_server" "virtual_server_21" {
  ...
}

resource "alteon_virtual_service" "virtual_service_21_443_https" {
  ...
}

resource "alteon_virtual_service" "virtual_service_21_80_http" {
  ...
}
```

This makes the generated Terraform easier to read and review.

---

## Requirements

* Python 3.11+
* Terraform 1.5+
* Radware Alteon Terraform Provider


This converter requires the Alteon Terraform provider:

* https://github.com/thomaselsaesser/terraform-provider-alteon/

---

## Installation

```bash
git clone https://github.com/team-netz/alteon-to-terraform.git
cd alteon-to-terraform
```

No external Python dependencies are required.

---

## Usage

Generate Terraform:

```bash
python3 converter/alteon_to_terraform.py alteon.cfg -o main.tf
```

Generate Terraform and Imports:

```bash
python3 converter/alteon_to_terraform.py \
  alteon.cfg \
  -o main.tf \
  -i import.tf
```

CLI-only export:

```bash
python3 converter/alteon_to_terraform.py \
  alteon.cfg \
  --cli-only
```

---

## Compatibility

### Alteon Firmware

Tested with:

* Alteon 31.x
* Alteon 32.x
* Alteon 33.x

### Terraform Provider

Compatible with:

* Radware Alteon Terraform Provider
* Thomas Elsaesser Alteon Provider Fork

---

## License

Apache License 2.0

Copyright (c) 2026 Michael Schwenke
Team-Netz GmbH

Licensed under the Apache License, Version 2.0.

http://www.apache.org/licenses/LICENSE-2.0

---

## Author

Michael Schwenke
Team-Netz GmbH

Repository:

https://github.com/team-netz/alteon-to-terraform

---

## Disclaimer

This project is not affiliated with, endorsed by, or supported by Radware.

Generated Terraform configurations should always be reviewed before deployment into production environments.

Use at your own risk.
