# Alteon Configuration to Terraform Converter

Convert Radware Alteon configuration dumps into Terraform resources using the Radware Alteon Terraform Provider.

## Overview

This tool parses Radware Alteon configuration dumps and generates Terraform resources that can be used to manage existing Alteon load balancer configurations through Terraform.

The converter focuses on Server Load Balancing (SLB) objects and generates native Terraform resources whenever supported by the provider. Unsupported or currently unmapped objects are exported as `alteon_cli_command` resources.

The generated Terraform code is intended as a migration and onboarding tool for existing Alteon environments.

---

## Features

### Native Terraform Resources

The converter currently supports:

| Alteon Configuration    | Terraform Resource       |
| ----------------------- | ------------------------ |
| `/c/slb/real`           | `alteon_real_server`     |
| `/c/slb/group`          | `alteon_server_group`    |
| `/c/slb/virt`           | `alteon_virtual_server`  |
| `/c/slb/virt/<service>` | `alteon_virtual_service` |
| `/c/slb/ssl/sslpol`     | `alteon_ssl_policy`      |
| `/c/slb/http2/*`        | `alteon_http2_policy`    |

---

### CLI Fallback Resources

The following objects are currently exported as `alteon_cli_command` resources:

| Alteon Configuration     |
| ------------------------ |
| `/c/slb/filt`            |
| `/c/slb/advhc/health`    |
| `/c/slb/ssl/certs/group` |
| `/c/l3/vrrp/vr`          |
| unsupported SLB objects  |

---

### Import Generation

The converter can generate Terraform import blocks for:

* Real Servers
* Server Groups
* Virtual Servers
* Virtual Services
* SSL Policies
* HTTP/2 Policies

This simplifies onboarding of existing Alteon configurations into Terraform state.

---

### Grouped Output

Virtual services are automatically grouped below their corresponding virtual server:

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

This improves readability and makes reviewing generated configurations easier.

---

## Requirements

* Python 3.11 or newer
* Terraform 1.5+
* Alteon Terraform Provider

---

## Installation

Clone the repository:

```bash
git clone https://github.com/team-netz/alteon-to-terraform.git
cd alteon-to-terraform
```

No additional Python dependencies are required.

---

## Usage

### Generate Terraform Configuration

```bash
python3 alteon_to_terraform_flat_v4_3.py alteon.cfg -o main.tf
```

### Generate Terraform Configuration and Import Blocks

```bash
python3 alteon_to_terraform_flat_v4_3.py \
    alteon.cfg \
    -o main.tf \
    -i import.tf
```

### CLI Only Mode

Export all supported objects as `alteon_cli_command` resources:

```bash
python3 alteon_to_terraform_flat_v4_3.py \
    alteon.cfg \
    -o main.tf \
    --cli-only
```

---

## Command Line Options

| Option              | Description                                          |
| ------------------- | ---------------------------------------------------- |
| `input`             | Alteon configuration dump file                       |
| `-o, --output`      | Terraform output file (default: `main.tf`)           |
| `-i, --import-file` | Generate Terraform import blocks                     |
| `--cli-only`        | Export all objects as `alteon_cli_command` resources |

---

## Example

### Alteon Configuration

```text
/c/slb/group 1030
    ipver v4
    metric roundrobin
    health icmp
    add 101102-a
    add 101103
    name "test_server_group_1030"
```

### Generated Terraform

```hcl
resource "alteon_server_group" "server_group_1030" {
  index = "1030"

  servers = [
    "101102-a",
    "101103"
  ]

  name               = "test_server_group_1030"
  metric             = "roundrobin"
  health_check_layer = "icmp"
  ip_ver             = 1
}
```

---

## Generated Import Blocks

Example:

```hcl
import {
  to = alteon_real_server.real_server_101102
  id = "101102"
}

import {
  to = alteon_server_group.server_group_1030
  id = "1030"
}

import {
  to = alteon_virtual_server.virtual_server_1000
  id = "1000"
}

import {
  to = alteon_virtual_service.virtual_service_1000_443_https
  id = "1000/443"
}
```

---

## Supported Server Group Attributes

The converter currently maps:

* `servers`
* `name`
* `metric`
* `health_check_layer`
* `health_id`
* `backup_server`
* `backup_group`
* `real_threshold`
* `slowstart`
* `ip_ver`

Example:

```text
/c/slb/group 22
    ipver v4
    metric roundrobin
    health icmp
    add 41
    add 42
    name "application_pool"
```

becomes:

```hcl
resource "alteon_server_group" "server_group_22" {
  index = "22"

  servers = [
    "41",
    "42"
  ]

  name               = "application_pool"
  metric             = "roundrobin"
  health_check_layer = "icmp"
  ip_ver             = 1
}
```

---

## Current Object Coverage

| Object                 | Status       |
| ---------------------- | ------------ |
| Real Servers           | Native       |
| Server Groups          | Native       |
| Virtual Servers        | Native       |
| Virtual Services       | Native       |
| SSL Policies           | Native       |
| HTTP/2 Policies        | Native       |
| Advanced Health Checks | CLI Fallback |
| SSL Certificate Groups | CLI Fallback |
| Filters                | CLI Fallback |
| VRRP                   | CLI Fallback |

---

## Limitations

### Not Converted

The following configuration sections are intentionally ignored:

* SSL private keys
* Certificate requests
* Certificate payloads
* Management configuration
* Routing configuration
* Layer 2 configuration
* Unsupported SLB objects

### Review Required

Generated Terraform configurations should always be reviewed before deployment.

Provider versions and Alteon firmware releases may introduce configuration differences that require manual adjustments.

---

## Compatibility

### Alteon Firmware

Tested with:

* Alteon 31.x
* Alteon 32.x
* Alteon 33.x

### Terraform Providers

Compatible with:

* Radware Alteon Terraform Provider
* Thomas Elsaesser Alteon Provider Fork

---

## License

Apache License 2.0

Copyright (c) 2026 Michael Schwenke
Team-Netz GmbH

Licensed under the Apache License, Version 2.0.

You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

---

## Author

Michael Schwenke
Team-Netz GmbH

---

## Disclaimer

This project is not affiliated with, endorsed by, or supported by Radware.

Use at your own risk.
