# Alteon Configuration to Terraform Converter

Convert Radware Alteon configuration dumps into Terraform resources using the Radware Alteon Terraform Provider.

## Overview

This tool parses an Alteon configuration dump and generates Terraform resources that can be used to manage an existing Alteon load balancer infrastructure through Terraform.

The converter focuses on Server Load Balancing (SLB) objects and creates native Terraform resources whenever possible. Unsupported objects are exported as generic `alteon_cli_command` resources.

## Features

### Native Terraform Resources

The converter currently supports:

| Alteon Configuration    | Terraform Resource       |
| ----------------------- | ------------------------ |
| `/c/slb/real`           | `alteon_real_server`     |
| `/c/slb/group`          | `alteon_server_group`    |
| `/c/slb/virt`           | `alteon_virtual_server`  |
| `/c/slb/virt/<service>` | `alteon_virtual_service` |

### Fallback Resources

The following objects are currently exported as CLI commands:

| Alteon Configuration     | Terraform Resource   |
| ------------------------ | -------------------- |
| `/c/slb/filt`            | `alteon_cli_command` |
| `/c/slb/ssl/certs/group` | `alteon_cli_command` |

### Import Generation

The converter can generate Terraform import blocks for:

* Real Servers
* Server Groups
* Virtual Servers

This simplifies onboarding of existing Alteon configurations into Terraform state.

## Requirements

* Python 3.11 or newer
* Terraform 1.5+
* Radware Alteon Terraform Provider

## Installation

Clone the repository:

```bash
git clone https://github.com/team-netz/alteon-to-terraform.git
cd alteon-to-terraform
```

No additional Python dependencies are required.

## Usage

### Generate Terraform Configuration

```bash
python3 alteon_to_terraform_native_v3_6.py alteon.cfg -o main.tf
```

### Generate Terraform Configuration and Import Blocks

```bash
python3 alteon_to_terraform_native_v3_6.py \
    alteon.cfg \
    -o main.tf \
    -i import.tf
```

### CLI Only Mode

Export everything as `alteon_cli_command` resources:

```bash
python3 alteon_to_terraform_native_v3_6.py \
    alteon.cfg \
    -o main.tf \
    --cli-only
```

## Command Line Options

| Option              | Description                                |
| ------------------- | ------------------------------------------ |
| `input`             | Alteon configuration dump file             |
| `-o, --output`      | Terraform output file (default: `main.tf`) |
| `-i, --import-file` | Generate Terraform import blocks           |
| `--cli-only`        | Export all objects as `alteon_cli_command` |

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
```

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

## Limitations

### Not Converted

The following configuration sections are intentionally ignored:

* SSL private keys
* Certificate requests
* Certificate payloads
* Management configuration
* Routing configuration
* Unsupported SLB objects

### Review Required

Generated Terraform should always be reviewed before deployment.

Provider versions and Alteon firmware releases may introduce configuration differences that require manual adjustments.

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

## License

Apache License 2.0

Copyright (c) 2026 Michael Schwenke
Team-Netz GmbH

Licensed under the Apache License, Version 2.0.

You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

## Author

Michael Schwenke
Team-Netz GmbH

## Disclaimer

This project is not affiliated with, endorsed by, or supported by Radware.

Use at your own risk.
