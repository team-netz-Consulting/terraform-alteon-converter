#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# =============================================================================
# Alteon Configuration to Terraform Converter
# =============================================================================
#
# Project:
# Alteon Configuration Converter
#
# Description:
# Converts Radware Alteon configuration dumps into Terraform resources
# using the Radware Alteon Terraform Provider.
#
# Supported Objects:
# - /c/slb/real
# - /c/slb/real/layer7
# - /c/slb/group
# - /c/slb/virt
# - /c/slb/virt/service
# - /c/slb/ssl/sslpol
# - /c/slb/ssl/certs/group
# - /c/slb/advhc/health
# - /c/slb/filt
# - /c/slb/pip
# - /c/slb/dataclass
# - /c/slb/contentclass
# - /c/slb/appshape
# - /c/l3/vrrp/vr
# - /c/l3/vrrp/vrgroup
#
# Generated Terraform Resources:
# - alteon_real_server
# - alteon_real_server_layer7
# - alteon_server_group
# - alteon_virtual_server
# - alteon_virtual_service
# - alteon_filter
# - alteon_advhc_*
# - alteon_ssl_policy
# - alteon_ssl_cert
# - alteon_ssl_cert_group
# - alteon_http2_policy
# - alteon_pip
# - alteon_data_class
# - alteon_content_class
# - alteon_appshape_script
# - alteon_appshape_binding
# - alteon_vrrp
# - alteon_vrrp_group
# - alteon_cli_command (fallback for unsupported objects)
#
# Author:
# Michael Schwenke
#
# Company:
# Team-Netz GmbH
#
# Repository:
# https://github.com/team-netz/alteon-to-terraform
#
# Version:
# 0.4.8
#
# Release Date:
# 2026-06-22
#
# Python Version:
# >= 3.11
#
# Terraform Provider:
# Radware/alteon
#
# Compatibility:
# Alteon 31.x
# Alteon 32.x
# Alteon 33.x
#
# License:
# Apache License 2.0
#
# Copyright:
# Copyright (c) 2026 Michael Schwenke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Disclaimer:
# This software is provided without any warranty. Generated Terraform
# configurations should always be reviewed before deployment to
# production environments.
#
# Changelog:
# 0.4.9
# - Fixed alteon_real_server_layer7 output to use real_server and exclude_str provider fields
# - Fixed alteon_virtual_service DBind, PBind, XForwardedFor, and ServCertGrpMark enum mappings
# - Fixed alteon_ssl_policy AdminStatus, Convert, Fessl, Bessl, TLS, PassInfo, and cipher enum mappings
# - Added provider-compatible CertBmap and UrlBmap decoding for certificate groups and real server Layer 7 URLs
#
# 0.4.8
# - Updated documentation and import coverage for native provider 4.8 resources
# - Merged known /c/slb/filt subcontexts into native alteon_filter resources
# - Merged VRRP subcontexts into native VRRP resources instead of CLI fallback
# - Kept native AdvHC, SSL cert/group, AppShape, PIP, data/content class mappings out of CLI fallback
# - Added native /c/slb/real <id>/layer7 conversion and import generation
#
# 0.4.7
# - Added native /c/slb/advhc/health conversion and import generation
# - Added native alteon_filter conversion and import generation
# - Added native data/content class and AppShape conversion/import generation
# - Added native alteon_pip conversion and import generation
#
# 0.4.6
# - Added VRRP group virtual_routers mapping from /c/l3/vrrp/vrgroup add entries
#
# 0.4.5
# - Fixed alteon_virtual_service key handling: index is service ordinal, virt_port is listener port
# - Fixed virtual service import ID format to <servindex>/<service_index>
#
# 0.4.4
# - Added native alteon_vrrp and alteon_vrrp_group conversion
# - Merge /c/l3/vrrp/*/track blocks into native VRRP resources
# - Added Terraform import generation for VRRP resources
#
# 0.4.3
# - Group virtual servers and their virtual services together in output
#
# 0.4.1
# - Added /c/slb/advhc/health detection
# - Added SSL certificate group handling
# - Improved SSL policy conversion
# - Added support for VRRP configuration detection
#
# 0.4.2
# - Added native alteon_server_group support using declarative servers set
#
# 0.4.0
# - Migrated to flat provider resource model
# - Added alteon_ssl_policy resource support
# - Added alteon_http2_policy resource support
# - Added native alteon_virtual_service mapping
# - Added import generation for SSL policies
#
# 0.3.6
# - Restrict alteon_server_group output to declarative provider schema
# - Map group ipver v4/v6 to ip_ver 1/2
# - Map group health <layer> to health_check_layer
# - Keep group metric as normalized provider string
#
# 0.3.4
# - Adapted alteon_server_group to declarative servers list model
# - Groups are now rendered as one resource with flat attributes
#
# 0.3.3
# - Added schema support for alteon_real_server
#
# 0.3.2
# - Added Terraform import file generation (-i/--import-file)
# - Added extended alteon_virtual_server field mapping
#
# 0.3.0
# - Added alteon_server_group support
# - Added alteon_virtual_service support
# - Added SSL service merging
# - Added /c/slb/filt detection
#
# 0.2.0
# - Added native alteon_virtual_server resources
# - Added native alteon_real_server resources
#
# 0.1.0
# - Initial implementation
# - CLI command based export
#
# =============================================================================

"""

alteon_to_terraform.py
Version: 0.4.8

Converts selected Radware Alteon configuration sections into
Terraform resources for the Alteon Terraform Provider.

Currently supported:

Native Resources:
- /c/slb/real                    -> alteon_real_server
- /c/slb/real/layer7             -> alteon_real_server_layer7
- /c/slb/group                   -> alteon_server_group
- /c/slb/virt                    -> alteon_virtual_server
- /c/slb/virt/service            -> alteon_virtual_service
- /c/slb/filt                    -> alteon_filter
- /c/slb/advhc/health            -> alteon_advhc_*
- /c/slb/pip                     -> alteon_pip
- /c/slb/dataclass              -> alteon_data_class
- /c/slb/contentclass           -> alteon_content_class
- /c/slb/appshape               -> alteon_appshape_script / alteon_appshape_binding
- /c/slb/ssl/sslpol             -> alteon_ssl_policy
- /c/slb/ssl/certs/*            -> alteon_ssl_cert / alteon_ssl_cert_group
- /c/slb/http2/*                -> alteon_http2_policy
- /c/l3/vrrp/vr                  -> alteon_vrrp
- /c/l3/vrrp/vrgroup             -> alteon_vrrp_group

CLI Fallback Resources:
- unsupported /c/slb/advhc/health types
- certificate/key/request payload imports

Import generation:
- alteon_real_server
- alteon_real_server_layer7
- alteon_server_group
- alteon_virtual_server
- alteon_virtual_service
- alteon_filter
- alteon_advhc_*
- alteon_pip
- alteon_data_class
- alteon_content_class
- alteon_appshape_script
- alteon_appshape_binding
- alteon_ssl_policy
- alteon_ssl_cert
- alteon_ssl_cert_group
- alteon_http2_policy
- alteon_vrrp
- alteon_vrrp_group

Intentionally ignored:
- Private keys
- Certificate payloads
- Certificate requests
- Unsupported Alteon contexts

Enum Mapping:

```
Enable:
    ena / enabled / e -> 2
    dis / disabled / d -> 3

IP Version:
    v4 -> 1
    v6 -> 2

Import IDs:
    Real Server      -> <index>
    Real Server L7   -> <index>
    Server Group     -> <index>
    Virtual Server   -> <index>
    Filter           -> <index>
    AdvHC            -> <id_name>
    SSL Policy       -> <name>
    SSL Cert         -> <cert_id>/<cert_type>
    SSL Cert Group   -> <group_id>
    Virtual Service  -> <virt_id>/<service_index>
    PIP              -> <address>
    Data Class       -> <id_name>
    Content Class    -> <id_name>
    AppShape Script  -> <index>
    AppShape Binding -> service:<virt>/<service_index>/<priority> or filter:<filter>/<priority>
    VRRP             -> <index>
    VRRP Group       -> <index>
```

"""
from __future__ import annotations

import argparse
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

__author__ = "Michael Schwenke"
__company__ = "Team-Netz GmbH"
__version__ = "0.4.8"
__license__ = "Apache-2.0"
__status__ = "Development"


ENABLE_MAP = {
    "ena": 2,
    "enabled": 2,
    "enable": 2,
    "e": 2,
    "on": 2,
    "dis": 3,
    "disabled": 3,
    "disable": 3,
    "d": 3,
    "off": 3,
}

BOOL_ENABLE_MAP = {
    "ena": 1,
    "enabled": 1,
    "enable": 1,
    "e": 1,
    "on": 1,
    "dis": 2,
    "disabled": 2,
    "disable": 2,
    "d": 2,
    "off": 2,
}


@dataclass
class Block:
    path: str
    commands: list[str] = field(default_factory=list)


def parse_alteon_config(text: str) -> list[Block]:
    blocks: list[Block] = []
    current: Block | None = None
    in_pem_or_text_import = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        if stripped.startswith("-----BEGIN "):
            in_pem_or_text_import = True
            continue
        if stripped.startswith("-----END "):
            in_pem_or_text_import = False
            continue
        if in_pem_or_text_import:
            continue

        if stripped.startswith("/*") or (stripped.startswith("script ") and (not current or "/appshape" not in current.path)):
            continue

        if stripped.startswith("/c/") or stripped == "/":
            if current:
                blocks.append(current)
            current = None
            if stripped == "/":
                continue
            current = Block(path=stripped)
            continue

        if current:
            current.commands.append(stripped)

    if current:
        blocks.append(current)

    return blocks


def split_cmd(cmd: str) -> list[str]:
    try:
        return shlex.split(cmd)
    except ValueError:
        return cmd.split()


def parse_commands(commands: list[str]) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for cmd in commands:
        parts = split_cmd(cmd)
        if not parts:
            continue
        key = parts[0].lower()
        parsed.setdefault(key, []).append(" ".join(parts[1:]))
    return parsed


def one_value(parsed: dict[str, list[str]], key: str) -> str | None:
    values = parsed.get(key.lower())
    if not values:
        return None
    return values[-1]


def clean_quote(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


def as_int_or_enum(value: str | None, enum_map: dict[str, int] | None = None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if enum_map:
        return enum_map.get(value.lower())
    return None


def enum_enable(value: str | None) -> int | None:
    return as_int_or_enum(value, ENABLE_MAP)


def enum_bool_enable(value: str | None) -> int | None:
    return as_int_or_enum(value, BOOL_ENABLE_MAP)


def decode_hex_bitmap(value: str | None) -> list[int]:
    value = clean_quote(value)
    if not value:
        return []
    items: list[int] = []
    for byte_idx, hex_byte in enumerate(value.split(":")):
        try:
            byte_value = int(hex_byte or "0", 16)
        except ValueError:
            byte_value = 0
        for bit in range(8):
            if byte_value & (1 << (7 - bit)):
                items.append(byte_idx * 8 + bit)
    return items


def parse_int_set_value(value: str | None) -> list[int]:
    value = clean_quote(value)
    if not value:
        return []
    if re.fullmatch(r"[0-9A-Fa-f]{0,2}(?::[0-9A-Fa-f]{0,2})+", value):
        return decode_hex_bitmap(value)

    items: list[int] = []
    for part in re.split(r"[\s,]+", value):
        item = as_int_or_enum(clean_quote(part))
        if item is not None:
            items.append(item)
    return items


def append_unique_ints(target: list[int], values: Iterable[int]) -> None:
    seen = set(target)
    for value in values:
        if value not in seen:
            target.append(value)
            seen.add(value)


def ipver_to_number(value: str | None) -> int | None:
    """New flat provider convention: 1=IPv4, 2=IPv6."""
    value = clean_quote(value)
    if not value:
        return None
    v = value.lower().strip()
    mapping = {"v4": 1, "ipv4": 1, "4": 1, "1": 1, "v6": 2, "ipv6": 2, "6": 2, "2": 2}
    return mapping.get(v)


def hcl_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return "[" + ", ".join(hcl_value(v) for v in value) + "]"
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def hcl_resource(resource_type: str, name: str, attrs: dict[str, Any]) -> list[str]:
    lines = [f'resource "{resource_type}" "{safe_name(name)}" {{']
    for key, value in attrs.items():
        if value is None:
            continue
        lines.append(f"  {key} = {hcl_value(value)}")
    lines.append("}")
    return lines


def hcl_resource_with_blocks(
    resource_type: str,
    name: str,
    attrs: dict[str, Any],
    blocks: dict[str, list[dict[str, Any]]] | None = None,
) -> list[str]:
    lines = [f'resource "{resource_type}" "{safe_name(name)}" {{']
    for key, value in attrs.items():
        if value is None:
            continue
        lines.append(f"  {key} = {hcl_value(value)}")
    for block_name, entries in (blocks or {}).items():
        for entry in entries:
            lines.append(f"  {block_name} {{")
            for key, value in entry.items():
                if value is None:
                    continue
                lines.append(f"    {key} = {hcl_value(value)}")
            lines.append("  }")
    lines.append("}")
    return lines


def safe_name(value: str) -> str:
    name = re.sub(r'["\s/.-]+', "_", value)
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_").lower()
    if not name:
        name = "resource"
    if re.match(r"^\d", name):
        name = f"r_{name}"
    return name


def unique_name(base: str, used: set[str]) -> str:
    name = safe_name(base)
    original = name
    i = 2
    while name in used:
        name = f"{original}_{i}"
        i += 1
    used.add(name)
    return name


def cli_line(block: Block) -> str:
    return "/".join([block.path] + block.commands)


def path_id(pattern: str, path: str) -> str | None:
    m = re.fullmatch(pattern, path)
    if not m:
        return None
    return m.group(1)


def is_real_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/real\s+[^/\s]+", path))


def is_real_subpath(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/real\s+\S+/.+", path))


def is_real_layer7_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/real\s+\S+/layer7", path))


def is_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/group\s+\S+", path))


def is_filter_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/filt\s+\d+", path))


def is_filter_subpath(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/filt\s+\d+/.+", path))


def is_virt_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/virt\s+\S+", path))


def parse_service_header(path: str) -> tuple[str, int, str | None, str | None] | None:
    # /c/slb/virt 21/service 443 https
    # /c/slb/virt 21/service 443 https/http
    # /c/slb/virt 21/service 443 https/ssl
    m = re.fullmatch(r"/c/slb/virt\s+(\S+)/service\s+(\d+)(?:\s+([^/]+))?(?:/(.+))?", path)
    if not m:
        return None
    virt_id = m.group(1)
    port = int(m.group(2))
    proto = m.group(3).strip() if m.group(3) else None
    suffix = m.group(4)
    return virt_id, port, proto, suffix


def is_virt_service_path(path: str) -> bool:
    return bool(parse_service_header(path))


def is_ssl_policy_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/ssl/sslpol\s+[^/\s]+(?:/.+)?", path))


SSL_CERT_TYPE_MAP = {
    "cert": 3,
    "certificate": 3,
    "server": 3,
    "servercert": 3,
    "servercertificate": 3,
    "trusted": 4,
    "trustedca": 4,
    "trustedcert": 4,
    "trustedcertificate": 4,
    "intermca": 5,
    "intermediate": 5,
    "intermediateca": 5,
    "ca": 5,
}


def ssl_cert_type(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    if value.isdigit():
        return int(value)
    return SSL_CERT_TYPE_MAP.get(value.lower().replace("-", "").replace("_", ""))


def parse_ssl_cert_path(path: str) -> tuple[str, int] | None:
    m = re.fullmatch(r"/c/slb/ssl/certs/(cert|certificate|trustedca|trusted|intermca)\s+([^/\s]+)", path)
    if not m:
        return None
    cert_type = ssl_cert_type(m.group(1))
    if cert_type is None:
        return None
    return m.group(2), cert_type


def is_ssl_cert_path(path: str) -> bool:
    return parse_ssl_cert_path(path) is not None


def is_http2_policy_path(path: str) -> bool:
    return bool(
        re.fullmatch(r"/c/slb/(?:accel/)?http2/(?:pol|policy)\s+\S+(?:/.+)?", path)
        or re.fullmatch(r"/c/slb/http2pol\s+\S+(?:/.+)?", path)
    )


def is_vrrp_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/l3/vrrp/vr\s+[^/\s]+", path))


def is_vrrp_subpath(path: str) -> bool:
    return bool(re.fullmatch(r"/c/l3/vrrp/vr\s+[^/\s]+/.+", path))


def is_vrrp_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/l3/vrrp/(?:vrgroup|group)\s+[^/\s]+", path))


def is_vrrp_group_subpath(path: str) -> bool:
    return bool(re.fullmatch(r"/c/l3/vrrp/(?:vrgroup|group)\s+[^/\s]+/.+", path))


def is_pip_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/pip(?:/(?:type|add)(?:\s+.+)?)?", path))


def parse_data_class_path(path: str) -> tuple[str, str | None, str | None] | None:
    m = re.fullmatch(r"/c/slb/(?:data[-_]?class|dataclass|dclass)\s+([^/\s]+)(?:/(?:manual|entry|entries)(?:\s+([^/\s]+))?)?", path)
    if not m:
        return None
    return m.group(1), "entry" if m.group(2) else None, m.group(2)


def is_data_class_path(path: str) -> bool:
    return parse_data_class_path(path) is not None


def parse_content_class_path(path: str) -> tuple[str, str | None, str | None] | None:
    prefix = r"/c/slb/(?:content[-_]?class|contentclass|contclass|class|l7/content[-_]?class|layer7/content[-_]?class)"
    m = re.fullmatch(prefix + r"\s+([^/\s]+)(?:/([^/\s]+)(?:\s+([^/\s]+))?)?", path)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def is_content_class_path(path: str) -> bool:
    return parse_content_class_path(path) is not None


def parse_appshape_script_path(path: str) -> str | None:
    m = re.fullmatch(r"/c/slb/appshape(?:/script)?\s+([^/\s]+)", path)
    return m.group(1) if m else None


def is_appshape_script_path(path: str) -> bool:
    return parse_appshape_script_path(path) is not None


def parse_appshape_binding_path(path: str) -> tuple[str, str | None, int | None, int | None, int | None] | None:
    service = re.fullmatch(r"/c/slb/virt\s+([^/\s]+)/service\s+\d+(?:\s+[^/]+)?/appshape(?:\s+(\d+))?", path)
    if service:
        return "service", service.group(1), None, None, as_int_or_enum(service.group(2))
    filt = re.fullmatch(r"/c/slb/filt\s+(\d+)/appshape(?:\s+(\d+))?", path)
    if filt:
        return "filter", None, None, int(filt.group(1)), as_int_or_enum(filt.group(2))
    bind = re.fullmatch(r"/c/slb/appshape/bind\s+(service|filter)\s+(.+)", path)
    if not bind:
        return None
    parts = split_cmd(bind.group(2))
    if bind.group(1) == "filter" and len(parts) >= 2:
        return "filter", None, None, as_int_or_enum(parts[0]), as_int_or_enum(parts[1])
    if bind.group(1) == "service" and len(parts) >= 3:
        return "service", parts[0], as_int_or_enum(parts[1]), None, as_int_or_enum(parts[2])
    return None


def is_appshape_binding_path(path: str) -> bool:
    return parse_appshape_binding_path(path) is not None


def is_advhc_health_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/advhc/health\s+\S+(?:\s+\S+)?(?:/.+)?", path))


def parse_advhc_health_path(path: str) -> tuple[str, str | None, str | None] | None:
    m = re.fullmatch(r"/c/slb/advhc/health\s+([^/\s]+)(?:\s+([^/\s]+))?(?:/(.+))?", path)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def is_ssl_cert_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/ssl/certs/group\s+\S+", path))


def is_cli_supported_path(path: str) -> bool:
    return bool(
        is_advhc_health_path(path)
        or is_filter_subpath(path)
        or (is_real_subpath(path) and not is_real_layer7_path(path))
        or is_pip_path(path)
        or is_data_class_path(path)
        or is_content_class_path(path)
        or is_appshape_script_path(path)
        or is_appshape_binding_path(path)
        or is_vrrp_subpath(path)
        or is_vrrp_group_subpath(path)
    )


def block_to_real_server(block: Block) -> tuple[str, list[str]] | None:
    index = path_id(r"/c/slb/real\s+(\S+)", block.path)
    if not index:
        return None

    parsed = parse_commands(block.commands)
    ipaddr = clean_quote(one_value(parsed, "rip") or one_value(parsed, "ipaddr"))
    if not ipaddr:
        return None

    attrs: dict[str, Any] = {
        "index": index,
        "ip_addr": ipaddr,
        "ip_ver": ipver_to_number(one_value(parsed, "ipver")),
        "name": clean_quote(one_value(parsed, "name")),
    }

    if "ena" in parsed:
        attrs["state"] = 2
    elif "dis" in parsed:
        attrs["state"] = 3

    string_keys = {
        "ipv6addr": "ipv6_addr",
        "proxyipaddress": "proxy_ip_addr",
        "proxyipaddr": "proxy_ip_addr",
        "proxyipmask": "proxy_ip_mask",
        "proxyipv6address": "proxy_ipv6_addr",
        "proxyipv6addr": "proxy_ipv6_addr",
        "proxyipnwclass": "proxy_ip_n_wclass",
        "oid": "oid",
        "commstring": "comm_string",
        "backup": "back_up",
        "health": "health_id",
        "healthid": "health_id",
        "hcid": "health_id",
    }
    int_keys = {
        "weight": "weight",
        "maxconns": "max_conns",
        "maxconn": "max_conns",
        "timeout": "time_out",
        "pinginterval": "ping_interval",
        "pingint": "ping_interval",
        "failretry": "fail_retry",
        "succretry": "succ_retry",
        "type": "type",
        "cookie": "cookie",
        "excludestr": "exclude_str",
        "submac": "submac",
        "idsport": "idsport",
        "nxtrportidx": "nxt_rport_idx",
        "nxtbuddyidx": "nxt_buddy_idx",
        "llbtype": "llb_type",
        "vlaningress": "vlan_ingress",
        "vlanegress": "vlan_egress",
        "egressif": "egress_if",
        "sectype": "sec_type",
        "ingressif": "ingress_if",
        "secdeviceflag": "sec_device_flag",
        "ingport": "ingport",
        "proxy": "proxy",
        "ldapwr": "ldapwr",
        "idsvlan": "idsvlan",
        "avail": "avail",
        "fasthealthcheck": "fast_health_check",
        "subdmac": "subdmac",
        "overflow": "overflow",
        "bkppreempt": "bkp_preempt",
        "mode": "mode",
        "proxyipmode": "proxy_ip_mode",
        "proxyipv6prefix": "proxy_ipv6_prefix",
        "proxyippersistency": "proxy_ip_persistency",
        "proxyipnwclasspersistency": "proxy_ip_n_wclass_persistency",
        "ingvlan": "ingvlan",
        "criticalconnthrsh": "critical_conn_thrsh",
        "highconnthrsh": "high_conn_thrsh",
        "uploadbandwidth": "upload_band_width",
        "downloadbandwidth": "download_band_width",
    }

    for cli_key, tf_key in string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            attrs[tf_key] = value

    for cli_key, tf_key in int_keys.items():
        value = as_int_or_enum(one_value(parsed, cli_key), ENABLE_MAP)
        if value is not None:
            attrs[tf_key] = value

    return f"real_server_{index}", hcl_resource("alteon_real_server", f"real_server_{index}", attrs)


def merge_real_server_layer7_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    real_layer7: dict[str, dict[str, Any]] = {}
    for block in blocks:
        index = path_id(r"/c/slb/real\s+(\S+)/layer7", block.path)
        if not index:
            continue

        parsed = parse_commands(block.commands)
        attrs = real_layer7.setdefault(index, {"real_server": index, "urls": []})

        exclude = clean_quote(one_value(parsed, "exclude") or one_value(parsed, "excludestr") or one_value(parsed, "exclude_str"))
        if exclude:
            exclude_str = as_int_or_enum(exclude, BOOL_ENABLE_MAP)
            if exclude_str is not None:
                attrs["exclude_str"] = exclude_str

        for key in ("addlb", "addurl", "add"):
            for value in parsed.get(key, []):
                append_unique_ints(attrs["urls"], parse_int_set_value(value))

        for key in ("urlbmap", "urls"):
            value = clean_quote(one_value(parsed, key))
            append_unique_ints(attrs["urls"], parse_int_set_value(value))

    for data in real_layer7.values():
        data["urls"] = sorted(data.get("urls", []))
        if not data["urls"]:
            data.pop("urls", None)
    return real_layer7


def real_server_layer7_to_hcl(index: str, attrs: dict[str, Any]) -> tuple[str, list[str]]:
    res_name = f"real_server_layer7_{index}"
    return res_name, hcl_resource("alteon_real_server_layer7", res_name, attrs)



def cli_bool(value: str | None) -> bool | None:
    """Mappt Alteon CLI enable/disable-Werte auf Terraform bool."""
    value = clean_quote(value)
    if not value:
        return None
    v = value.lower().strip()
    if v in {"ena", "enabled", "enable", "e", "on", "yes", "true", "1"}:
        return True
    if v in {"dis", "disabled", "disable", "d", "off", "no", "false", "2", "0"}:
        return False
    return None


def vrrp_version(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    v = value.lower().strip()
    if v in {"v4", "ipv4", "4", "1"}:
        return "v4"
    if v in {"v6", "ipv6", "6", "2"}:
        return "v6"
    return None


def parse_vrrp_track(commands: list[str]) -> dict[str, Any]:
    parsed = parse_commands(commands)
    attrs: dict[str, Any] = {}

    # Alteon track CLI shorthand -> provider bool fields.
    mapping = {
        "vrs": "track_virt_rtr",
        "virt": "track_virt_rtr",
        "virtrtr": "track_virt_rtr",
        "ifs": "track_ip_intf",
        "if": "track_ip_intf",
        "intf": "track_ip_intf",
        "ports": "track_vlan_port",
        "port": "track_vlan_port",
        "vlan": "track_vlan_port",
        "l4": "track_l4_port",
        "real": "track_real_server",
        "rserver": "track_real_server",
        "hsrp": "track_hsrp",
        "hsrv": "track_hsrv",
        "swext": "track_sw_ext",
        "isl": "track_isl_port_include",
    }

    for cli_key, tf_key in mapping.items():
        value = cli_bool(one_value(parsed, cli_key))
        if value is not None:
            attrs[tf_key] = value

    return attrs


def merge_vrrp_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    vrrps: dict[str, dict[str, Any]] = {}
    for block in blocks:
        m = re.fullmatch(r"/c/l3/vrrp/vr\s+([^/\s]+)(?:/(.+))?", block.path)
        if not m:
            continue
        index = m.group(1)
        suffix = m.group(2)
        data = vrrps.setdefault(index, {"index": index, "base": [], "track": []})
        if suffix == "track":
            data["track"].extend(block.commands)
        elif suffix:
            data["base"].extend(block.commands)
        else:
            data["base"].extend(block.commands)
    return vrrps


def merge_vrrp_group_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for block in blocks:
        m = re.fullmatch(r"/c/l3/vrrp/(?:vrgroup|group)\s+([^/\s]+)(?:/(.+))?", block.path)
        if not m:
            continue
        index = m.group(1)
        suffix = m.group(2)
        data = groups.setdefault(index, {"index": index, "base": [], "track": []})
        if suffix == "track":
            data["track"].extend(block.commands)
        elif suffix:
            data["base"].extend(block.commands)
        else:
            data["base"].extend(block.commands)
    return groups


def vrrp_common_attrs(index: str, base_commands: list[str], track_commands: list[str], include_addr: bool) -> dict[str, Any]:
    parsed = parse_commands(base_commands)

    index_int = as_int_or_enum(index)
    attrs: dict[str, Any] = {
        "index": index_int if index_int is not None else index,
    }

    vrid = as_int_or_enum(one_value(parsed, "vrid") or one_value(parsed, "id"))
    if vrid is None:
        # Provider requires vrid. Alteon vrgroup configs often omit it; use the
        # table index as safe default.
        vrid = index_int
    if vrid is not None:
        attrs["vrid"] = vrid

    version = vrrp_version(one_value(parsed, "ipver") or one_value(parsed, "version"))
    if version:
        attrs["version"] = version

    if include_addr:
        addr = clean_quote(one_value(parsed, "addr"))
        if addr:
            if version == "v6":
                attrs["ipv6_addr"] = addr
            else:
                attrs["addr"] = addr

    for cli_key, tf_key in {
        "if": "if_index",
        "ifindex": "if_index",
        "adver": "interval",
        "interval": "interval",
        "prio": "priority",
        "priority": "priority",
        "ipv6interval": "ipv6_interval",
        "ospfcost": "ospf_cost",
    }.items():
        value = as_int_or_enum(one_value(parsed, cli_key))
        if value is not None:
            attrs[tf_key] = value

    # State may be represented either as standalone "ena/dis" commands or as a
    # keyed "state ena/dis" value.
    if "ena" in parsed:
        attrs["state"] = True
    elif "dis" in parsed:
        attrs["state"] = False
    else:
        state = cli_bool(one_value(parsed, "state"))
        if state is not None:
            attrs["state"] = state

    for cli_key, tf_key in {
        "preem": "preempt",
        "preempt": "preempt",
        "share": "sharing",
        "sharing": "sharing",
    }.items():
        value = cli_bool(one_value(parsed, cli_key))
        if value is not None:
            attrs[tf_key] = value

    attrs.update(parse_vrrp_track(track_commands))
    return attrs


def vrrp_to_hcl(index: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    attrs = vrrp_common_attrs(index, data.get("base", []), data.get("track", []), include_addr=True)
    res_name = f"vrrp_{index}"
    return res_name, hcl_resource("alteon_vrrp", res_name, attrs)


def vrrp_group_to_hcl(index: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    attrs = vrrp_common_attrs(index, data.get("base", []), data.get("track", []), include_addr=False)

    # /c/l3/vrrp/vrgroup <id>
    #     add 251
    #     add 248
    #
    # Provider schema: virtual_routers = [251, 248]
    parsed = parse_commands(data.get("base", []))
    virtual_routers: list[int] = []
    for value in parsed.get("add", []):
        vr_index = as_int_or_enum(value)
        if vr_index is not None:
            virtual_routers.append(vr_index)

    if virtual_routers:
        attrs["virtual_routers"] = virtual_routers

    res_name = f"vrrp_group_{index}"
    return res_name, hcl_resource("alteon_vrrp_group", res_name, attrs)


def pip_kind(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().strip()
    if normalized in {"vlan", "vlans"}:
        return "vlans"
    if normalized in {"port", "ports"}:
        return "ports"
    return None


def add_pip_assignment(pips: dict[str, dict[str, Any]], kind: str | None, value: str | None) -> None:
    if kind not in {"ports", "vlans"} or not value:
        return

    parts = split_cmd(value)
    if len(parts) < 2:
        return

    address = clean_quote(parts[0])
    assignment = as_int_or_enum(parts[1])
    if not address or assignment is None:
        return

    data = pips.setdefault(address, {"address": address, "ports": [], "vlans": []})
    if assignment not in data[kind]:
        data[kind].append(assignment)


def merge_pip_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    pips: dict[str, dict[str, Any]] = {}
    current_kind: str | None = None

    for block in blocks:
        if not is_pip_path(block.path):
            continue

        type_match = re.fullmatch(r"/c/slb/pip/type\s+(\S+)", block.path)
        if type_match:
            current_kind = pip_kind(type_match.group(1))
            continue

        add_match = re.fullmatch(r"/c/slb/pip/add\s+(.+)", block.path)
        if add_match:
            add_pip_assignment(pips, current_kind, add_match.group(1))
            continue

        parsed = parse_commands(block.commands)
        for value in parsed.get("type", []):
            kind = pip_kind(value)
            if kind:
                current_kind = kind
        for value in parsed.get("add", []):
            add_pip_assignment(pips, current_kind, value)

    return pips


def pip_to_hcl(address: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    attrs: dict[str, Any] = {"address": address}
    ports = sorted(data.get("ports", []))
    vlans = sorted(data.get("vlans", []))
    if ports:
        attrs["ports"] = ports
    if vlans:
        attrs["vlans"] = vlans
    res_name = f"pip_{address}"
    return res_name, hcl_resource("alteon_pip", res_name, attrs)


def data_class_type(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().strip()
    if normalized in {"ip", "ipv4", "address", "2"}:
        return "ip"
    if normalized in {"string", "str", "1"}:
        return "string"
    return None


def add_data_class_entry(data: dict[str, Any], entry_id: int | None, value: str | None) -> None:
    parts = split_cmd(value or "")
    if entry_id is None:
        if len(parts) < 2:
            return
        entry_id = as_int_or_enum(parts[0])
        parts = parts[1:]
    if entry_id is None or not parts:
        return
    entry: dict[str, Any] = {"id": entry_id, "key": clean_quote(parts[0])}
    if len(parts) > 1:
        entry["value"] = clean_quote(" ".join(parts[1:]))
    data.setdefault("entry", {})[entry_id] = entry


def merge_data_class_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    classes: dict[str, dict[str, Any]] = {}
    for block in blocks:
        parsed_path = parse_data_class_path(block.path)
        if not parsed_path:
            continue
        dc_id, suffix, entry_id_raw = parsed_path
        data = classes.setdefault(dc_id, {"attrs": {"id_name": dc_id}, "entry": {}})
        parsed = parse_commands(block.commands)

        if suffix == "entry":
            entry_id = as_int_or_enum(entry_id_raw)
            key = clean_quote(one_value(parsed, "key"))
            if key and entry_id is not None:
                entry = {"id": entry_id, "key": key}
                value = clean_quote(one_value(parsed, "value") or one_value(parsed, "val"))
                if value:
                    entry["value"] = value
                data["entry"][entry_id] = entry
            for value in parsed.get("add", []):
                add_data_class_entry(data, entry_id, value)
            continue

        attrs = data["attrs"]
        name = clean_quote(one_value(parsed, "name"))
        if name:
            attrs["name"] = name
        dtype = data_class_type(one_value(parsed, "type") or one_value(parsed, "datatype") or one_value(parsed, "data_type"))
        if dtype:
            attrs["data_type"] = dtype
        default = cli_bool(one_value(parsed, "default"))
        if default is not None:
            attrs["default"] = default
        for value in parsed.get("add", []) + parsed.get("entry", []):
            add_data_class_entry(data, None, value)

    return classes


def data_class_to_hcl(dc_id: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    entries = sorted(data.get("entry", {}).values(), key=lambda item: int(item["id"]))
    res_name = f"data_class_{dc_id}"
    return res_name, hcl_resource_with_blocks("alteon_data_class", res_name, data["attrs"], {"entry": entries})


CONTENT_MATCH_TYPES = ("hostname", "path", "filename", "filetype", "header", "cookie", "text", "xml")
URL_MATCH_REVERSE = {"1": "sufx", "2": "prefx", "3": "equal", "4": "include", "5": "regex"}
HDR_MATCH_REVERSE = {"3": "equal", "4": "include", "5": "regex"}
TEXT_MATCH_REVERSE = {"4": "include", "5": "regex"}
TEXT_LOOKUP_REVERSE = {"1": "header", "2": "body", "3": "both"}
XML_NAME_REVERSE = {"1": "sufx", "3": "equal"}
XML_VAL_REVERSE = {"1": "sufx", "3": "equal", "4": "include"}


def enum_word(value: str | None, reverse: dict[str, str]) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().strip()
    return reverse.get(normalized, normalized)


def add_content_entry(data: dict[str, Any], kind: str | None, entry_id: str | None, commands: list[str], inline: str | None = None) -> None:
    if kind not in CONTENT_MATCH_TYPES:
        return
    parsed = parse_commands(commands)
    parts = split_cmd(inline or "")
    if not entry_id and parts:
        entry_id = clean_quote(parts[0])
        parts = parts[1:]
    if not entry_id:
        entry_id = str(len(data.setdefault(kind, [])) + 1)

    entry: dict[str, Any] = {"id": entry_id}
    if kind == "hostname":
        entry["host_name"] = clean_quote(one_value(parsed, "hostname") or one_value(parsed, "host") or (parts[0] if parts else None))
        entry["match_type"] = enum_word(one_value(parsed, "match") or one_value(parsed, "matchtype") or (parts[1] if len(parts) > 1 else None), URL_MATCH_REVERSE)
        entry["data_class_id"] = clean_quote(one_value(parsed, "dataclass") or one_value(parsed, "data_class_id"))
    elif kind == "path":
        entry["file_path"] = clean_quote(one_value(parsed, "path") or one_value(parsed, "file") or one_value(parsed, "filepath") or (parts[0] if parts else None))
        entry["match_type"] = enum_word(one_value(parsed, "match") or one_value(parsed, "matchtype") or (parts[1] if len(parts) > 1 else None), URL_MATCH_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
        entry["data_class_id"] = clean_quote(one_value(parsed, "dataclass") or one_value(parsed, "data_class_id"))
    elif kind == "filename":
        entry["file_name"] = clean_quote(one_value(parsed, "filename") or one_value(parsed, "name") or (parts[0] if parts else None))
        entry["match_type"] = enum_word(one_value(parsed, "match") or one_value(parsed, "matchtype") or (parts[1] if len(parts) > 1 else None), URL_MATCH_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
    elif kind == "filetype":
        entry["file_type"] = clean_quote(one_value(parsed, "filetype") or one_value(parsed, "type") or (parts[0] if parts else None))
        entry["match_type"] = enum_word(one_value(parsed, "match") or one_value(parsed, "matchtype") or (parts[1] if len(parts) > 1 else None), URL_MATCH_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
    elif kind == "header":
        entry["name"] = clean_quote(one_value(parsed, "name") or (parts[0] if parts else None))
        entry["value"] = clean_quote(one_value(parsed, "value") or one_value(parsed, "val") or (parts[1] if len(parts) > 1 else None))
        entry["match_type_name"] = enum_word(one_value(parsed, "matchname") or one_value(parsed, "match_type_name"), HDR_MATCH_REVERSE)
        entry["match_type_val"] = enum_word(one_value(parsed, "matchval") or one_value(parsed, "match_type_val"), HDR_MATCH_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
    elif kind == "cookie":
        entry["key"] = clean_quote(one_value(parsed, "key") or (parts[0] if parts else None))
        entry["value"] = clean_quote(one_value(parsed, "value") or one_value(parsed, "val") or (parts[1] if len(parts) > 1 else None))
        entry["match_type_key"] = enum_word(one_value(parsed, "matchkey") or one_value(parsed, "match_type_key"), HDR_MATCH_REVERSE)
        entry["match_type_val"] = enum_word(one_value(parsed, "matchval") or one_value(parsed, "match_type_val"), HDR_MATCH_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
    elif kind == "text":
        entry["text"] = clean_quote(one_value(parsed, "text") or (parts[0] if parts else None))
        entry["match_type"] = enum_word(one_value(parsed, "match") or one_value(parsed, "matchtype"), TEXT_MATCH_REVERSE)
        entry["lookup_area"] = enum_word(one_value(parsed, "lookup") or one_value(parsed, "lookuparea"), TEXT_LOOKUP_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))
    elif kind == "xml":
        entry["tag_name"] = clean_quote(one_value(parsed, "tag") or one_value(parsed, "tagname") or (parts[0] if parts else None))
        entry["tag_value"] = clean_quote(one_value(parsed, "value") or one_value(parsed, "tagval") or (parts[1] if len(parts) > 1 else None))
        entry["match_type_name"] = enum_word(one_value(parsed, "matchname") or one_value(parsed, "match_type_name"), XML_NAME_REVERSE)
        entry["match_type_val"] = enum_word(one_value(parsed, "matchval") or one_value(parsed, "match_type_val"), XML_VAL_REVERSE)
        entry["case"] = cli_bool(one_value(parsed, "case"))

    required = {
        "hostname": "host_name",
        "path": "file_path",
        "filename": "file_name",
        "filetype": "file_type",
        "header": "name",
        "cookie": "key",
        "text": "text",
        "xml": "tag_name",
    }[kind]
    if entry.get(required):
        data.setdefault(kind, []).append(entry)


def merge_content_class_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    classes: dict[str, dict[str, Any]] = {}
    for block in blocks:
        parsed_path = parse_content_class_path(block.path)
        if not parsed_path:
            continue
        cc_id, suffix, entry_id = parsed_path
        data = classes.setdefault(cc_id, {"attrs": {"id_name": cc_id}})
        parsed = parse_commands(block.commands)
        if suffix in CONTENT_MATCH_TYPES:
            add_content_entry(data, suffix, entry_id, block.commands)
            continue
        attrs = data["attrs"]
        name = clean_quote(one_value(parsed, "name"))
        if name:
            attrs["name"] = name
        cc_type = as_int_or_enum(one_value(parsed, "type"))
        if cc_type is not None:
            attrs["type"] = cc_type
        logical = clean_quote(one_value(parsed, "logical") or one_value(parsed, "logical_expression") or one_value(parsed, "logexp"))
        if logical:
            attrs["logical_expression"] = logical
        for kind in CONTENT_MATCH_TYPES:
            for value in parsed.get(kind, []):
                add_content_entry(data, kind, None, [], value)
    return classes


def content_class_to_hcl(cc_id: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    blocks = {kind: data.get(kind, []) for kind in CONTENT_MATCH_TYPES if data.get(kind)}
    res_name = f"content_class_{cc_id}"
    return res_name, hcl_resource_with_blocks("alteon_content_class", res_name, data["attrs"], blocks)


def appshape_bool(value: str | None) -> bool | None:
    return cli_bool(value)


def merge_appshape_script_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    scripts: dict[str, dict[str, Any]] = {}
    for block in blocks:
        index = parse_appshape_script_path(block.path)
        if not index:
            continue
        parsed = parse_commands(block.commands)
        attrs = scripts.setdefault(index, {"index": index})
        name = clean_quote(one_value(parsed, "name"))
        if name:
            attrs["name"] = name
        state = appshape_bool(one_value(parsed, "state"))
        if state is None:
            if "ena" in parsed:
                state = True
            elif "dis" in parsed:
                state = False
        if state is not None:
            attrs["state"] = state
        default = cli_bool(one_value(parsed, "default"))
        if default is not None:
            attrs["default"] = default
    return scripts


def appshape_script_to_hcl(index: str, attrs: dict[str, Any]) -> tuple[str, list[str]]:
    res_name = f"appshape_script_{index}"
    return res_name, hcl_resource("alteon_appshape_script", res_name, attrs)


def add_appshape_binding(bindings: dict[str, dict[str, Any]], attrs: dict[str, Any]) -> None:
    target = attrs.get("target")
    priority = attrs.get("priority")
    script = attrs.get("script_index")
    if not target or priority is None or not script:
        return
    if target == "filter":
        key = f"filter_{attrs.get('filter')}_{priority}"
    else:
        key = f"service_{attrs.get('virtual_server')}_{attrs.get('virtual_service')}_{priority}"
    bindings[key] = attrs


def merge_appshape_binding_blocks(blocks: list[Block], service_data: dict[tuple[str, int, str | None], dict[str, Any]]) -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for block in blocks:
        parsed_path = parse_appshape_binding_path(block.path)
        if not parsed_path:
            continue
        target, virt, service_index, filt, priority = parsed_path
        parsed = parse_commands(block.commands)
        script = clean_quote(one_value(parsed, "script") or one_value(parsed, "index") or one_value(parsed, "script_index"))
        if not script and parsed.get("add"):
            parts = split_cmd(parsed["add"][-1])
            if priority is None and parts:
                priority = as_int_or_enum(parts[0])
                parts = parts[1:]
            if parts:
                script = clean_quote(parts[-1])
        if priority is None:
            priority = as_int_or_enum(one_value(parsed, "priority"))
        if target == "service":
            header = parse_service_header(block.path)
            if header:
                key = (header[0], header[1], header[2])
                service_index = int(service_data.get(key, {}).get("service_index") or 1)
                virt = header[0]
            attrs = {
                "target": "service",
                "virtual_server": virt,
                "virtual_service": service_index,
                "priority": priority,
                "script_index": script,
            }
        else:
            attrs = {
                "target": "filter",
                "filter": filt,
                "priority": priority,
                "script_index": script,
            }
        add_appshape_binding(bindings, attrs)
    return bindings


def appshape_binding_to_hcl(key: str, attrs: dict[str, Any]) -> tuple[str, list[str]]:
    return f"appshape_binding_{key}", hcl_resource("alteon_appshape_binding", f"appshape_binding_{key}", attrs)


ADVHC_TYPE_MAP = {
    "tcp": "tcp",
    "icmp": "icmp",
    "udp": "udp",
    "dns": "dns",
    "http": "http",
    "https": "http",
    "smtp": "smtp",
    "sslhello": "sslhello",
    "ssl_hello": "sslhello",
    "ssl-hello": "sslhello",
    "ldap": "ldap",
    "ldaps": "ldap",
    "radius": "radius",
    "arp": "arp",
    "link": "link",
    "script": "script",
}

ADVHC_ENUMS = {
    "conn_term": {"1": "fin", "fin": "fin", "2": "rst", "rst": "rst"},
    "conn_tout": {"1": "fin", "fin": "fin", "2": "rst", "rst": "rst"},
    "transport": {"1": "tcp", "tcp": "tcp", "2": "udp", "udp": "udp"},
    "method": {"1": "get", "get": "get", "2": "post", "post": "post", "3": "head", "head": "head"},
    "auth_level": {"1": "none", "none": "none", "2": "basic", "basic": "basic", "3": "ntlm2", "ntlm2": "ntlm2", "4": "ntlmssp", "ntlmssp": "ntlmssp"},
    "response_type": {"1": "none", "none": "none", "2": "incl", "incl": "incl", "include": "incl", "4": "excl", "excl": "excl", "exclude": "excl"},
    "overload_type": {"1": "none", "none": "none", "2": "incl", "incl": "incl", "include": "incl"},
    "https_cipher_name": {"1": "user_defined", "user-defined": "user_defined", "user_defined": "user_defined", "2": "low", "low": "low", "3": "medium", "medium": "medium", "4": "high", "high": "high"},
}


def advhc_type(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    return ADVHC_TYPE_MAP.get(value.lower().replace("-", "_"))


def advhc_ip_version(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    v = value.lower()
    if v in {"v4", "ipv4", "4", "1"}:
        return 4
    if v in {"v6", "ipv6", "6", "2"}:
        return 6
    return None


def advhc_enum(field: str, value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    return ADVHC_ENUMS.get(field, {}).get(value.lower().replace("_", "-"))


def set_advhc_string(attrs: dict[str, Any], parsed: dict[str, list[str]], keys: list[str], tf_key: str) -> None:
    for key in keys:
        value = clean_quote(one_value(parsed, key))
        if value:
            attrs[tf_key] = value
            return


def set_advhc_int(attrs: dict[str, Any], parsed: dict[str, list[str]], keys: list[str], tf_key: str) -> None:
    for key in keys:
        value = as_int_or_enum(one_value(parsed, key))
        if value is not None:
            attrs[tf_key] = value
            return


def set_advhc_bool(attrs: dict[str, Any], parsed: dict[str, list[str]], keys: list[str], tf_key: str) -> None:
    for key in keys:
        value = cli_bool(one_value(parsed, key))
        if value is not None:
            attrs[tf_key] = value
            return


def set_advhc_enum(attrs: dict[str, Any], parsed: dict[str, list[str]], keys: list[str], tf_key: str) -> None:
    for key in keys:
        value = advhc_enum(tf_key, one_value(parsed, key))
        if value:
            attrs[tf_key] = value
            return


def apply_advhc_commands(attrs: dict[str, Any], hc_type: str, commands: list[str], suffix: str | None = None) -> None:
    parsed = parse_commands(commands)

    set_advhc_string(attrs, parsed, ["name"], "name")
    dport = port_number(one_value(parsed, "dport") or one_value(parsed, "port"))
    if dport is not None:
        attrs["dport"] = dport
    ip_ver = advhc_ip_version(one_value(parsed, "ipver") or one_value(parsed, "ip_version"))
    if ip_ver is not None:
        attrs["ip_version"] = ip_ver
    set_advhc_string(attrs, parsed, ["hostname", "host_name"], "host_name")
    for cli_keys, tf_key in [
        (["transparent"], "transparent"),
        (["invert"], "invert"),
        (["snat"], "snat"),
    ]:
        set_advhc_bool(attrs, parsed, cli_keys, tf_key)
    for cli_keys, tf_key in [
        (["interval"], "interval"),
        (["retries"], "retries"),
        (["restoreretries", "restore_retries"], "restore_retries"),
        (["timeout"], "timeout"),
        (["overflow"], "overflow"),
        (["downinterval", "down_interval"], "down_interval"),
    ]:
        set_advhc_int(attrs, parsed, cli_keys, tf_key)

    if hc_type == "tcp":
        set_advhc_enum(attrs, parsed, ["connterm", "conn_term"], "conn_term")
        set_advhc_bool(attrs, parsed, ["always"], "always")
    elif hc_type == "udp":
        set_advhc_int(attrs, parsed, ["padding"], "padding")
    elif hc_type == "dns":
        set_advhc_string(attrs, parsed, ["domain", "domainname", "domain_name"], "domain_name")
        set_advhc_enum(attrs, parsed, ["transport"], "transport")
    elif hc_type == "http":
        if suffix and suffix.lower() == "http":
            pass
        set_advhc_bool(attrs, parsed, ["https", "ssl"], "https")
        set_advhc_string(attrs, parsed, ["host"], "host")
        set_advhc_string(attrs, parsed, ["path"], "path")
        set_advhc_enum(attrs, parsed, ["method"], "method")
        set_advhc_string(attrs, parsed, ["headers", "header"], "headers")
        set_advhc_string(attrs, parsed, ["body"], "body")
        set_advhc_enum(attrs, parsed, ["auth", "authlevel", "auth_level"], "auth_level")
        set_advhc_string(attrs, parsed, ["username", "user"], "username")
        set_advhc_string(attrs, parsed, ["password", "pass"], "password")
        set_advhc_enum(attrs, parsed, ["responsetype", "response_type"], "response_type")
        set_advhc_string(attrs, parsed, ["responsecode", "response_code"], "response_code")
        set_advhc_string(attrs, parsed, ["receivestring", "receive_string", "recv"], "receive_string")
        response = one_value(parsed, "response")
        if response:
            parts = split_cmd(response)
            if parts:
                attrs["response_code"] = clean_quote(parts[0])
            if len(parts) > 1:
                response_type = advhc_enum("response_type", parts[1])
                if response_type:
                    attrs["response_type"] = response_type
            if len(parts) > 2:
                receive = clean_quote(" ".join(parts[2:]))
                if receive:
                    attrs["receive_string"] = receive
        set_advhc_enum(attrs, parsed, ["overloadtype", "overload_type"], "overload_type")
        set_advhc_string(attrs, parsed, ["overloadstring", "overload_string"], "overload_string")
        set_advhc_string(attrs, parsed, ["responsecodeoverload", "response_code_overload"], "response_code_overload")
        set_advhc_bool(attrs, parsed, ["proxy"], "proxy")
        set_advhc_enum(attrs, parsed, ["cipher", "httpsciphername", "https_cipher_name"], "https_cipher_name")
        set_advhc_string(attrs, parsed, ["cipheruserdef", "https_cipher_userdef"], "https_cipher_userdef")
        set_advhc_bool(attrs, parsed, ["http2"], "http2")
        set_advhc_enum(attrs, parsed, ["conntout", "conn_tout"], "conn_tout")
    elif hc_type == "smtp":
        set_advhc_string(attrs, parsed, ["username", "user"], "username")
    elif hc_type == "sslhello":
        set_advhc_string(attrs, parsed, ["sslversion", "ssl_version"], "ssl_version")
        set_advhc_string(attrs, parsed, ["cipher", "ciphername", "cipher_name"], "cipher_name")
        set_advhc_string(attrs, parsed, ["cipheruserdef", "cipher_userdef"], "cipher_userdef")
    elif hc_type == "ldap":
        set_advhc_bool(attrs, parsed, ["ldaps", "ssl"], "ldaps")
        set_advhc_string(attrs, parsed, ["username", "user"], "username")
        set_advhc_string(attrs, parsed, ["password", "pass"], "password")
        set_advhc_string(attrs, parsed, ["baseobject", "base_object"], "base_object")
        set_advhc_string(attrs, parsed, ["basefmt", "base_fmt"], "base_fmt")
    elif hc_type == "radius":
        set_advhc_int(attrs, parsed, ["downtype", "down_type"], "down_type")
        set_advhc_string(attrs, parsed, ["username", "user"], "username")
        set_advhc_string(attrs, parsed, ["password", "pass"], "password")
        set_advhc_string(attrs, parsed, ["secret"], "secret")
    elif hc_type == "script":
        script = one_value(parsed, "string") or one_value(parsed, "stringval") or one_value(parsed, "string_val")
        if script:
            attrs["string_val"] = clean_quote(script)


def merge_advhc_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    for block in blocks:
        parsed_path = parse_advhc_health_path(block.path)
        if not parsed_path:
            continue
        name, raw_type, suffix = parsed_path
        hc_type = advhc_type(raw_type)
        data = checks.setdefault(name, {"type": hc_type, "attrs": {"id_name": name}, "raw": []})
        if hc_type and not data.get("type"):
            data["type"] = hc_type
        if raw_type and raw_type.lower() in {"https", "ldaps"}:
            data["attrs"]["https" if raw_type.lower() == "https" else "ldaps"] = True
        data["raw"].append(block)
        if data.get("type"):
            apply_advhc_commands(data["attrs"], data["type"], block.commands, suffix)
    return checks


def advhc_to_hcl(name: str, data: dict[str, Any]) -> tuple[str, list[str]] | None:
    hc_type = data.get("type")
    if not hc_type:
        return None
    res_type = f"alteon_advhc_{hc_type}"
    res_name = f"advhc_{hc_type}_{name}"
    return res_name, hcl_resource(res_type, res_name, data["attrs"])



GROUP_METRIC_MAP = {
    "1": "roundrobin",
    "roundrobin": "roundrobin",
    "rr": "roundrobin",
    "2": "leastconnections",
    "leastconnections": "leastconnections",
    "leastconns": "leastconnections",
    "leastconn": "leastconnections",
    "3": "minmisses",
    "minmisses": "minmisses",
    "minmiss": "minmisses",
    "4": "hash",
    "hash": "hash",
    "5": "response",
    "response": "response",
    "6": "bandwidth",
    "bandwidth": "bandwidth",
    "7": "phash",
    "phash": "phash",
    "8": "svcleast",
    "svcleast": "svcleast",
    "9": "hrw",
    "hrw": "hrw",
}

GROUP_HEALTH_LAYER_MAP = {
    "1": "icmp",
    "icmp": "icmp",
    "ping": "icmp",
    "2": "tcp",
    "tcp": "tcp",
    "3": "http",
    "http": "http",
    "44": "http",
    "httphead": "http",
    "4": "dns",
    "dns": "dns",
    "5": "smtp",
    "smtp": "smtp",
    "28": "link",
    "link": "link",
    "31": "ldap",
    "ldap": "ldap",
}


def normalize_group_metric(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().replace("-", "").replace("_", "")
    return GROUP_METRIC_MAP.get(normalized)


def normalize_group_health_layer(value: str | None) -> str | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().replace("-", "").replace("_", "")
    return GROUP_HEALTH_LAYER_MAP.get(normalized)


def block_to_server_group(block: Block) -> tuple[str, list[str]] | None:
    index = path_id(r"/c/slb/group\s+(\S+)", block.path)
    if not index:
        return None

    parsed = parse_commands(block.commands)
    attrs: dict[str, Any] = {"index": index}

    servers = [clean_quote(server) for server in parsed.get("add", [])]
    servers = [server for server in servers if server]
    if servers:
        attrs["servers"] = servers

    name = clean_quote(one_value(parsed, "name"))
    if name:
        attrs["name"] = name

    metric = normalize_group_metric(one_value(parsed, "metric"))
    if metric:
        attrs["metric"] = metric

    health_check_layer = (
        normalize_group_health_layer(one_value(parsed, "health"))
        or normalize_group_health_layer(one_value(parsed, "healthchecklayer"))
        or normalize_group_health_layer(one_value(parsed, "health_check_layer"))
        or normalize_group_health_layer(one_value(parsed, "healthck"))
        or normalize_group_health_layer(one_value(parsed, "hc"))
    )
    if health_check_layer:
        attrs["health_check_layer"] = health_check_layer

    health_id = (
        clean_quote(one_value(parsed, "healthid"))
        or clean_quote(one_value(parsed, "health_id"))
        or clean_quote(one_value(parsed, "hcid"))
    )
    if health_id:
        attrs["health_id"] = health_id

    backup_server = (
        clean_quote(one_value(parsed, "backupserver"))
        or clean_quote(one_value(parsed, "backup_server"))
    )
    if backup_server:
        attrs["backup_server"] = backup_server

    backup_group = (
        clean_quote(one_value(parsed, "backupgroup"))
        or clean_quote(one_value(parsed, "backup_group"))
    )
    if backup_group:
        attrs["backup_group"] = backup_group

    # Legacy/ambiguous "backup" is treated as backup_server only when no explicit
    # backup_server/backup_group was present.
    backup = clean_quote(one_value(parsed, "backup"))
    if backup and "backup_server" not in attrs and "backup_group" not in attrs:
        attrs["backup_server"] = backup

    for cli_key, tf_key in {
        "realthreshold": "real_threshold",
        "real_threshold": "real_threshold",
        "slowstart": "slowstart",
    }.items():
        value = as_int_or_enum(one_value(parsed, cli_key))
        if value is not None:
            attrs[tf_key] = value

    ip_ver = ipver_to_number(one_value(parsed, "ipver") or one_value(parsed, "ip_ver"))
    if ip_ver is not None:
        attrs["ip_ver"] = ip_ver

    res_name = f"server_group_{index}"
    return res_name, hcl_resource("alteon_server_group", res_name, attrs)


FILTER_ACTION_MAP = {
    "1": 1,
    "allow": 1,
    "permit": 1,
    "2": 2,
    "deny": 2,
    "drop": 2,
    "discard": 2,
    "3": 3,
    "redirect": 3,
    "redir": 3,
    "4": 4,
    "nat": 4,
    "5": 5,
    "goto": 5,
    "6": 6,
    "outboundllb": 6,
    "outbound-llb": 6,
    "7": 7,
    "monitor": 7,
}

FILTER_NAT_MAP = {
    "1": 1,
    "dest": 1,
    "dst": 1,
    "destination": 1,
    "destination-address": 1,
    "2": 2,
    "src": 2,
    "source": 2,
    "source-address": 2,
    "3": 3,
    "multicast": 3,
    "multicast-address": 3,
}

PROTOCOL_MAP = {
    "icmp": 1,
    "tcp": 6,
    "udp": 17,
    "gre": 47,
    "esp": 50,
    "ah": 51,
}

PORT_MAP = {
    "ftp": 21,
    "ssh": 22,
    "telnet": 23,
    "smtp": 25,
    "dns": 53,
    "http": 80,
    "pop3": 110,
    "ntp": 123,
    "imap": 143,
    "ldap": 389,
    "https": 443,
    "ldaps": 636,
}


def normalize_filter_action(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().replace("_", "-")
    return FILTER_ACTION_MAP.get(normalized)


def normalize_filter_nat(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower().replace("_", "-")
    return FILTER_NAT_MAP.get(normalized)


def protocol_number(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower()
    if normalized.isdigit():
        return int(normalized)
    return PROTOCOL_MAP.get(normalized)


def port_number(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    normalized = value.lower()
    if normalized in {"any", "all"}:
        return None
    if normalized.isdigit():
        return int(normalized)
    return PORT_MAP.get(normalized)


def add_filter_port_range(attrs: dict[str, Any], value: str | None, low_key: str, high_key: str) -> None:
    value = clean_quote(value)
    if not value:
        return
    parts = re.split(r"\s+|-", value, maxsplit=1)
    low = port_number(parts[0])
    high = port_number(parts[1]) if len(parts) > 1 else low
    if low is not None:
        attrs[low_key] = str(low)
    if high is not None:
        attrs[high_key] = str(high)


def apply_filter_commands(attrs: dict[str, Any], commands: list[str], suffix: str | None = None) -> None:
    parsed = parse_commands(commands)

    if "ena" in parsed:
        attrs["state"] = 2
    elif "dis" in parsed:
        attrs["state"] = 3
    else:
        state = as_int_or_enum(one_value(parsed, "state"), ENABLE_MAP)
        if state is not None:
            attrs["state"] = state

    for cli_key, tf_key in {
        "name": "name",
        "sip": "src_ip",
        "srcip": "src_ip",
        "src_ip": "src_ip",
        "smask": "src_ip_mask",
        "srcmask": "src_ip_mask",
        "src_mask": "src_ip_mask",
        "srcipmask": "src_ip_mask",
        "src_ip_mask": "src_ip_mask",
        "dip": "dst_ip",
        "dstip": "dst_ip",
        "dst_ip": "dst_ip",
        "dmask": "dst_ip_mask",
        "dstmask": "dst_ip_mask",
        "dst_mask": "dst_ip_mask",
        "dstipmask": "dst_ip_mask",
        "dst_ip_mask": "dst_ip_mask",
        "group": "redir_group",
        "redirgroup": "redir_group",
        "redirect_group": "redir_group",
        "redir_group": "redir_group",
    }.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value and value.lower() != "any":
            attrs[tf_key] = value

    proto = protocol_number(one_value(parsed, "proto") or one_value(parsed, "protocol"))
    if proto is not None:
        attrs["protocol"] = str(proto)

    add_filter_port_range(
        attrs,
        one_value(parsed, "sport") or one_value(parsed, "srcport") or one_value(parsed, "src_port"),
        "range_low_src_port",
        "range_high_src_port",
    )
    add_filter_port_range(
        attrs,
        one_value(parsed, "dport") or one_value(parsed, "dstport") or one_value(parsed, "dst_port"),
        "range_low_dst_port",
        "range_high_dst_port",
    )

    for cli_key, tf_key in {
        "sportlow": "range_low_src_port",
        "srcportlow": "range_low_src_port",
        "range_low_src_port": "range_low_src_port",
        "sporthigh": "range_high_src_port",
        "srcporthigh": "range_high_src_port",
        "range_high_src_port": "range_high_src_port",
        "dportlow": "range_low_dst_port",
        "dstportlow": "range_low_dst_port",
        "range_low_dst_port": "range_low_dst_port",
        "dporthigh": "range_high_dst_port",
        "dstporthigh": "range_high_dst_port",
        "range_high_dst_port": "range_high_dst_port",
        "rport": "redir_port",
        "redirport": "redir_port",
        "redirect_port": "redir_port",
        "redir_port": "redir_port",
        "goto": "goto_filter",
        "gotofilter": "goto_filter",
    }.items():
        if "port" in cli_key or cli_key == "rport":
            port = port_number(one_value(parsed, cli_key))
            value = str(port) if port is not None else None
        else:
            value = clean_quote(one_value(parsed, cli_key))
        if value is not None:
            attrs[tf_key] = value

    action = normalize_filter_action(one_value(parsed, "action"))
    if action:
        attrs["action"] = action

    nat = normalize_filter_nat(one_value(parsed, "nat"))
    if nat:
        attrs["nat"] = nat

    vlan = as_int_or_enum(one_value(parsed, "vlan"))
    if vlan is not None:
        attrs["vlan"] = str(vlan)

    for cli_key, tf_key in {
        "invert": "invert",
        "inv": "invert",
        "log": "log",
    }.items():
        value = as_int_or_enum(one_value(parsed, cli_key), ENABLE_MAP)
        if value is not None:
            attrs[tf_key] = value

    content_class = (
        clean_quote(one_value(parsed, "contentclass"))
        or clean_quote(one_value(parsed, "content_class"))
        or clean_quote(one_value(parsed, "layer7denyaddurl"))
        or clean_quote(one_value(parsed, "addurl"))
    )
    if content_class:
        attrs["cntclass"] = content_class

    if suffix:
        suffix = suffix.lower()

    if suffix and suffix.startswith("ssl"):
        sslpol = clean_quote(one_value(parsed, "sslpol"))
        if sslpol:
            attrs["ssl_policy"] = sslpol

        srvrcert = clean_quote(one_value(parsed, "srvrcert"))
        if srvrcert:
            parts = split_cmd(srvrcert)
            if len(parts) >= 2 and parts[0].lower() == "group":
                attrs["srv_cert"] = parts[-1]
                attrs["srv_cert_group"] = 1
            elif len(parts) >= 2 and parts[0].lower() == "cert":
                attrs["srv_cert"] = parts[-1]
                attrs["srv_cert_group"] = 0
            else:
                attrs["srv_cert"] = srvrcert

    if suffix and suffix.startswith("adv"):
        dbind = map_dbind(one_value(parsed, "dbind"))
        if dbind is not None:
            attrs["dbind"] = dbind

        rtproxy = as_int_or_enum(one_value(parsed, "rtproxy") or one_value(parsed, "return_to_proxy"), ENABLE_MAP)
        if rtproxy is not None:
            attrs["rtproxy"] = rtproxy

        rtsrcmac = as_int_or_enum(one_value(parsed, "rtsrcmac") or one_value(parsed, "return_to_src_mac"), ENABLE_MAP)
        if rtsrcmac is not None:
            attrs["rtsrcmac"] = rtsrcmac


def block_to_filter(block: Block) -> tuple[str, list[str]] | None:
    index = path_id(r"/c/slb/filt\s+(\d+)", block.path)
    if not index:
        return None

    attrs: dict[str, Any] = {"index": int(index)}
    apply_filter_commands(attrs, block.commands)
    res_name = f"filter_{index}"
    return res_name, hcl_resource("alteon_filter", res_name, attrs)


def merge_filter_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    filters: dict[str, dict[str, Any]] = {}
    for block in blocks:
        m = re.fullmatch(r"/c/slb/filt\s+(\d+)(?:/(.+))?", block.path)
        if not m:
            continue
        index = m.group(1)
        suffix = m.group(2)
        data = filters.setdefault(index, {"attrs": {"index": int(index)}, "paths": set()})
        data["paths"].add(block.path)
        apply_filter_commands(data["attrs"], block.commands, suffix)
    return filters


def filter_to_hcl(index: str, data: dict[str, Any]) -> tuple[str, list[str]]:
    res_name = f"filter_{index}"
    return res_name, hcl_resource("alteon_filter", res_name, data["attrs"])



def block_to_virtual_server(block: Block) -> tuple[str, list[str]] | None:
    index = path_id(r"/c/slb/virt\s+(\S+)", block.path)
    if not index:
        return None

    parsed = parse_commands(block.commands)
    vip = clean_quote(one_value(parsed, "vip") or one_value(parsed, "virt_server_ip_address"))
    if not vip:
        return None

    attrs: dict[str, Any] = {
        "index": index,
        "virt_server_ip_address": vip,
        "virt_server_ip_ver": ipver_to_number(one_value(parsed, "ipver")),
        "virt_server_vname": clean_quote(one_value(parsed, "name")),
    }

    if "ena" in parsed:
        attrs["virt_server_state"] = 2
    elif "dis" in parsed:
        attrs["virt_server_state"] = 3

    string_keys = {
        "dname": "virt_server_dname",
        "domain": "virt_server_dname",
        "ipv6": "virt_server_ipv6_addr",
        "ipv6addr": "virt_server_ipv6_addr",
        "srcnetwork": "virt_server_src_network",
        "nat": "virt_server_nat",
        "nat6": "virt_server_nat6",
        "wanlink": "virt_server_wanlink",
        "segment": "virt_server_segment",
    }
    int_keys = {
        "l3only": "virt_server_layer3_only",
        "layer3only": "virt_server_layer3_only",
        "bwmcontract": "virt_server_bwm_contract",
        "weight": "virt_server_weight",
        "avail": "virt_server_avail",
        "freeserviceidx": "virt_server_free_service_idx",
        "creset": "virt_server_c_reset",
        "isdnssecvip": "virt_server_is_dns_sec_vip",
        "availpersist": "virt_server_avail_persist",
        "rtsrcmac": "virt_server_rt_src_mac",
        "creationtype": "virt_server_creation_type",
        "dad": "virt_serverdad",
    }

    for cli_key, tf_key in string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            attrs[tf_key] = value

    for cli_key, tf_key in int_keys.items():
        value = as_int_or_enum(one_value(parsed, cli_key), ENABLE_MAP)
        if value is not None:
            attrs[tf_key] = value

    return f"virtual_server_{index}", hcl_resource("alteon_virtual_server", f"virtual_server_{index}", attrs)


def merge_service_blocks(blocks: list[Block]) -> dict[tuple[str, int, str | None], dict[str, Any]]:
    """
    Merge all /c/slb/virt <id>/service <port> ... subcontexts.

    Provider key semantics:
      servindex = virtual server index
      index     = ordinal service index on that virtual server (1, 2, ...)
      virt_port = actual listener port from Alteon CLI

    The dictionary key remains (virt_id, port, protocol), but each service gets
    a stable service_index assigned in source order per virtual server.
    """
    services: dict[tuple[str, int, str | None], dict[str, Any]] = {}
    service_order_by_virt: dict[str, list[tuple[str, int, str | None]]] = {}

    for block in blocks:
        parsed_header = parse_service_header(block.path)
        if not parsed_header:
            continue

        virt_id, port, proto, suffix = parsed_header
        key = (virt_id, port, proto)

        if key not in services:
            service_order_by_virt.setdefault(virt_id, []).append(key)
            services[key] = {
                "virt_id": virt_id,
                "port": port,
                "protocol": proto,
                "service_index": None,
                "base": [],
                "ssl": [],
                "http": [],
                "other": [],
                "paths": [],
            }

        data = services[key]
        data["paths"].append(block.path)
        if suffix == "ssl":
            data["ssl"].extend(block.commands)
        elif suffix == "http":
            data["http"].extend(block.commands)
        elif suffix:
            data["other"].extend(block.commands)
            # Encode some useful path-only subcommands like /pbind ... as raw context.
            data["other"].append(f"__path_suffix__ {suffix}")
        else:
            data["base"].extend(block.commands)

    for virt_id, keys in service_order_by_virt.items():
        for ordinal, key in enumerate(keys, start=1):
            services[key]["service_index"] = ordinal

    return services

def map_service_action(value: str | None) -> int | None:
    value = clean_quote(value)
    if not value:
        return None
    mapping = {
        "group": 1,
        "redirect": 2,
        "discard": 3,
    }
    return mapping.get(value.lower())


def map_dbind(value: str | None) -> int | None:
    return as_int_or_enum(
        value,
        {
            "ena": 1,
            "enable": 1,
            "enabled": 1,
            "on": 1,
            "dis": 2,
            "disable": 2,
            "disabled": 2,
            "off": 2,
            "forceproxy": 3,
            "force-proxy": 3,
        },
    )


def map_pbind(value: str | None) -> int | None:
    return as_int_or_enum(
        value,
        {
            "clientip": 2,
            "client-ip": 2,
            "client_ip": 2,
            "dis": 3,
            "disable": 3,
            "disabled": 3,
            "off": 3,
            "sslid": 4,
            "ssl-id": 4,
            "ssl_id": 4,
            "cookie": 5,
        },
    )


def service_to_hcl(data: dict[str, Any]) -> tuple[str, list[str]]:
    virt_id = data["virt_id"]
    port = data["port"]
    proto = data["protocol"]

    parsed = parse_commands(data["base"])
    parsed_ssl = parse_commands(data["ssl"])
    parsed_http = parse_commands(data["http"])
    parsed_other = parse_commands(data["other"])

    service_index = int(data.get("service_index") or 1)

    attrs: dict[str, Any] = {
        "servindex": virt_id,
        "index": service_index,
        "virt_port": int(port),
    }

    rport = as_int_or_enum(one_value(parsed, "rport"))
    if rport is not None:
        attrs["real_port"] = rport

    group = clean_quote(one_value(parsed, "group"))
    if group:
        attrs["real_group"] = group

    timeout = as_int_or_enum(one_value(parsed, "tmout") or one_value(parsed, "timeout"))
    if timeout is not None:
        attrs["time_out"] = timeout

    dbind = map_dbind(one_value(parsed, "dbind"))
    if dbind is not None:
        attrs["d_bind"] = dbind

    pbind_value = one_value(parsed, "pbind")
    if pbind_value is None:
        for suffix in reversed(parsed_other.get("__path_suffix__", [])):
            parts = split_cmd(suffix)
            if len(parts) >= 2 and parts[0].lower() == "pbind":
                pbind_value = parts[1]
                break
    pbind = map_pbind(pbind_value)
    if pbind is not None:
        attrs["p_bind"] = pbind

    action = map_service_action(one_value(parsed, "action"))
    if action is not None:
        attrs["action"] = action

    redirect = clean_quote(one_value(parsed, "redirect"))
    if redirect:
        attrs["redirect"] = redirect

    name = clean_quote(one_value(parsed, "name"))
    if name:
        attrs["name"] = name

    # HTTP sub-context.
    xff = enum_bool_enable(one_value(parsed_http, "xforward"))
    if xff is not None:
        attrs["x_forwarded_for"] = xff

    # SSL sub-context.
    sslpol = clean_quote(one_value(parsed_ssl, "sslpol"))
    if sslpol:
        attrs["ss_lpol"] = sslpol

    srvrcert = clean_quote(one_value(parsed_ssl, "srvrcert"))
    if srvrcert:
        parts = split_cmd(srvrcert)
        if len(parts) >= 2 and parts[0].lower() == "group":
            attrs["serv_cert"] = parts[-1]
            attrs["serv_cert_grp_mark"] = 2
        elif len(parts) >= 2 and parts[0].lower() == "cert":
            attrs["serv_cert"] = parts[-1]
            attrs["serv_cert_grp_mark"] = 1
        else:
            attrs["serv_cert"] = srvrcert

    res_name = f"virtual_service_{virt_id}_{port}_{proto or 'ip'}"
    return res_name, hcl_resource("alteon_virtual_service", res_name, attrs)


def merge_ssl_policy_blocks(blocks: list[Block]) -> dict[str, dict[str, list[str]]]:
    policies: dict[str, dict[str, list[str]]] = {}
    for block in blocks:
        m = re.fullmatch(r"/c/slb/ssl/sslpol\s+([^/\s]+)(?:/(.+))?", block.path)
        if not m:
            continue
        name = m.group(1)
        suffix = m.group(2) or "main"
        policies.setdefault(name, {}).setdefault(suffix, []).extend(block.commands)
    return policies


SSL_POLICY_FE_MODE_MAP = {
    "ena": 1,
    "enable": 1,
    "enabled": 1,
    "on": 1,
    "dis": 2,
    "disable": 2,
    "disabled": 2,
    "off": 2,
    "request": 3,
    "req": 3,
    "handshake": 4,
    "hs": 4,
}

SSL_POLICY_BE_MODE_MAP = {
    **SSL_POLICY_FE_MODE_MAP,
    "proxy": 5,
}

SSL_POLICY_CIPHER_MAP = {
    "rsa": 0,
    "all": 1,
    "all-non-null-ciphers": 2,
    "all_non_null_ciphers": 2,
    "sslv3": 3,
    "tlsv1": 4,
    "tlsv1-2": 5,
    "tlsv1_2": 5,
    "export": 6,
    "low": 7,
    "medium": 8,
    "high": 9,
    "rsa-rc4-128-md5": 10,
    "rsa-rc4-128-sha1": 11,
    "rsa-des-sha1": 12,
    "rsa-3des-sha1": 13,
    "rsa-aes-128-sha1": 14,
    "rsa-aes-256-sha1": 15,
    "pci-dss-compliance": 16,
    "pci_dss_compliance": 16,
    "user-defined": 17,
    "userdefined": 17,
    "user_defined": 17,
    "user-defined-expert": 18,
    "userdefinedexpert": 18,
    "user_defined_expert": 18,
    "main": 19,
    "http2": 20,
}

SSL_POLICY_BE_CIPHER_MAP = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "user-defined": 3,
    "userdefined": 3,
    "user_defined": 3,
    "user-defined-expert": 4,
    "userdefinedexpert": 4,
    "user_defined_expert": 4,
    "main": 5,
}


def parse_cipher_command(value: str | None) -> tuple[str | None, str | None]:
    value = clean_quote(value)
    if not value:
        return None, None
    parts = split_cmd(value)
    if len(parts) >= 2 and parts[0].lower() in {"user-defined", "userdefined", "user_defined", "user-defined-expert", "userdefinedexpert", "user_defined_expert"}:
        return parts[0].lower(), parts[1]
    return parts[0] if parts else value, None


def set_ssl_cipher_attrs(attrs: dict[str, Any], value: str | None, backend: bool = False) -> None:
    cipher_name, cipher_userdef = parse_cipher_command(value)
    if not cipher_name:
        return

    cipher_key = "becipher" if backend else "cipher_name"
    userdef_key = "be_cipher_userdef" if backend else "cipher_userdef"
    expert_key = "be_cipher_expert_userdef" if backend else "cipher_expert_userdef"
    cipher_map = SSL_POLICY_BE_CIPHER_MAP if backend else SSL_POLICY_CIPHER_MAP

    normalized = cipher_name.lower()
    cipher_value = as_int_or_enum(cipher_name, cipher_map)
    if cipher_value is not None:
        attrs[cipher_key] = cipher_value

    if cipher_userdef:
        if "expert" in normalized:
            attrs[expert_key] = cipher_userdef
        else:
            attrs[userdef_key] = cipher_userdef


def ssl_policy_to_hcl(name: str, sections: dict[str, list[str]]) -> tuple[str, list[str]]:
    main = parse_commands(sections.get("main", []))
    backend = parse_commands(sections.get("backend", []))
    passinfo = parse_commands(sections.get("passinfo", []))
    frver = parse_commands(sections.get("frver", []))
    bever = parse_commands(sections.get("backend/ver", []))

    attrs: dict[str, Any] = {"nameidindex": name}

    display_name = clean_quote(one_value(main, "name"))
    if display_name:
        attrs["name"] = display_name

    if "ena" in main:
        attrs["admin_status"] = 1
    elif "dis" in main:
        attrs["admin_status"] = 2

    convert = enum_bool_enable(one_value(main, "convert"))
    if convert is not None:
        attrs["convert"] = convert

    fessl = as_int_or_enum(one_value(main, "fessl"), SSL_POLICY_FE_MODE_MAP)
    if fessl is not None:
        attrs["fessl"] = fessl

    set_ssl_cipher_attrs(attrs, one_value(main, "cipher"))

    intermca = clean_quote(one_value(main, "intermca"))
    if intermca:
        parts = split_cmd(intermca)
        if len(parts) >= 2:
            attrs["intermca_chain_type"] = parts[0]
            attrs["intermca_chain_name"] = parts[1]

    secreneg = clean_quote(one_value(main, "secreneg"))
    if secreneg:
        attrs["secreneg"] = secreneg

    be_ssl = as_int_or_enum(one_value(backend, "ssl"), SSL_POLICY_BE_MODE_MAP)
    if be_ssl is not None:
        attrs["bessl"] = be_ssl

    set_ssl_cipher_attrs(attrs, one_value(backend, "cipher"), backend=True)

    pass_frontend = enum_bool_enable(one_value(passinfo, "frontend"))
    if pass_frontend is not None:
        attrs["pass_info_frontend"] = pass_frontend

    # TLS version subcontexts.
    for key, tf_key in {
        "tls10": "fe_tls10_version",
        "tls11": "fe_tls11_version",
        "tls12": "fe_tls12_version",
        "tls13": "fe_tls13_version",
        "sslv3": "fe_sslv3_version",
    }.items():
        value = enum_bool_enable(one_value(frver, key))
        if value is not None:
            attrs[tf_key] = value

    for key, tf_key in {
        "tls10": "be_tls10_version",
        "tls11": "be_tls11_version",
        "tls12": "be_tls12_version",
        "tls13": "be_tls13_version",
        "sslv3": "be_sslv3_version",
    }.items():
        value = enum_bool_enable(one_value(bever, key))
        if value is not None:
            attrs[tf_key] = value

    res_name = f"ssl_policy_{name}"
    return res_name, hcl_resource("alteon_ssl_policy", res_name, attrs)


def merge_ssl_cert_blocks(blocks: list[Block]) -> dict[tuple[str, int], dict[str, Any]]:
    certs: dict[tuple[str, int], dict[str, Any]] = {}
    for block in blocks:
        parsed_path = parse_ssl_cert_path(block.path)
        if not parsed_path:
            continue
        cert_id, cert_type = parsed_path
        parsed = parse_commands(block.commands)
        attrs = certs.setdefault((cert_id, cert_type), {"cert_id": cert_id, "cert_type": cert_type})

        for cli_key, tf_key in {
            "name": "name",
            "commonname": "common_name",
            "common_name": "common_name",
            "cn": "common_name",
            "country": "country_name",
            "countryname": "country_name",
            "country_name": "country_name",
            "province": "province_name",
            "provincename": "province_name",
            "province_name": "province_name",
            "locality": "locality_name",
            "localityname": "locality_name",
            "locality_name": "locality_name",
            "organization": "organization_name",
            "organizationname": "organization_name",
            "organization_name": "organization_name",
            "organizationunit": "organization_unit_name",
            "organizationunitname": "organization_unit_name",
            "organization_unit_name": "organization_unit_name",
            "email": "e_mail",
            "e_mail": "e_mail",
            "serial": "serial",
            "subjectaltname": "subject_alt_name",
            "subject_alt_name": "subject_alt_name",
            "expiry": "expiry",
            "expirty": "expirty",
            "intermca": "intermca_chain_name",
            "intermcachain": "intermca_chain_name",
            "intermca_chain_name": "intermca_chain_name",
        }.items():
            value = clean_quote(one_value(parsed, cli_key))
            if value:
                attrs[tf_key] = value

        for cli_key, tf_key in {
            "keysize": "key_size",
            "key_size": "key_size",
            "hashalgo": "hash_algo",
            "hash_algo": "hash_algo",
            "validity": "validity_period",
            "validityperiod": "validity_period",
            "validity_period": "validity_period",
            "status": "status",
            "keytype": "key_type",
            "key_type": "key_type",
            "keysizeec": "key_size_ec",
            "key_size_ec": "key_size_ec",
            "curvenameec": "curve_name_ec",
            "curve_name_ec": "curve_name_ec",
            "keysizecommon": "key_size_common",
            "key_size_common": "key_size_common",
            "intermcachaintype": "intermca_chain_type",
            "intermca_chain_type": "intermca_chain_type",
        }.items():
            value = as_int_or_enum(one_value(parsed, cli_key))
            if value is not None:
                attrs[tf_key] = value
    return certs


def ssl_cert_to_hcl(cert_id: str, cert_type: int, attrs: dict[str, Any]) -> tuple[str, list[str]]:
    res_name = f"ssl_cert_{cert_id}_{cert_type}"
    return res_name, hcl_resource("alteon_ssl_cert", res_name, attrs)


def merge_ssl_cert_group_blocks(blocks: list[Block]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for block in blocks:
        group_id = path_id(r"/c/slb/ssl/certs/group\s+(\S+)", block.path)
        if not group_id:
            continue
        parsed = parse_commands(block.commands)
        attrs = groups.setdefault(group_id, {"group_id": group_id, "certificates": []})

        name = clean_quote(one_value(parsed, "name"))
        if name:
            attrs["name"] = name

        group_type = ssl_cert_type(one_value(parsed, "type"))
        if group_type is not None:
            attrs["type"] = group_type

        default_cert = clean_quote(one_value(parsed, "default") or one_value(parsed, "defaultcert") or one_value(parsed, "default_cert"))
        if default_cert:
            attrs["default_cert"] = default_cert

        for cli_key, tf_key in {
            "configtype": "config_type",
            "config_type": "config_type",
            "chaining": "chaining_mode",
            "chainingmode": "chaining_mode",
            "chaining_mode": "chaining_mode",
        }.items():
            value = as_int_or_enum(one_value(parsed, cli_key))
            if value is not None:
                attrs[tf_key] = value

        for key in ("add", "addcert"):
            for value in parsed.get(key, []):
                append_unique_ints(attrs["certificates"], parse_int_set_value(value))

        for key in ("certbmap", "certificates"):
            append_unique_ints(attrs["certificates"], parse_int_set_value(one_value(parsed, key)))

    for data in groups.values():
        data["certificates"] = sorted(data.get("certificates", []))
        if not data["certificates"]:
            data.pop("certificates", None)
    return groups


def ssl_cert_group_to_hcl(group_id: str, attrs: dict[str, Any]) -> tuple[str, list[str]]:
    res_name = f"ssl_cert_group_{group_id}"
    return res_name, hcl_resource("alteon_ssl_cert_group", res_name, attrs)


def merge_http2_policy_blocks(blocks: list[Block]) -> dict[str, list[str]]:
    policies: dict[str, list[str]] = {}
    for block in blocks:
        m = re.fullmatch(r"/c/slb/(?:accel/)?http2/(?:pol|policy)\s+(\S+)(?:/.+)?", block.path)
        if not m:
            m = re.fullmatch(r"/c/slb/http2pol\s+(\S+)(?:/.+)?", block.path)
        if not m:
            continue
        policies.setdefault(m.group(1), []).extend(block.commands)
    return policies


def http2_policy_to_hcl(name: str, commands: list[str]) -> tuple[str, list[str]]:
    parsed = parse_commands(commands)
    attrs: dict[str, Any] = {"nameidindex": name}
    string_keys = {"name": "name", "header": "header", "hpack": "hpack_size", "backendhpack": "backend_hpack_size"}
    int_keys = {
        "ena": "admin_status",
        "admin": "admin_status",
        "streams": "streams",
        "idle": "idle",
        "enainsert": "ena_insert",
        "serverpush": "ena_server_push",
        "backend": "backend_status",
        "backendstreams": "backend_streams",
    }
    if "ena" in parsed:
        attrs["admin_status"] = 2
    elif "dis" in parsed:
        attrs["admin_status"] = 3
    for cli_key, tf_key in string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            attrs[tf_key] = value
    for cli_key, tf_key in int_keys.items():
        if cli_key in {"ena"}:
            continue
        value = as_int_or_enum(one_value(parsed, cli_key), ENABLE_MAP)
        if value is not None:
            attrs[tf_key] = value
    res_name = f"http2_policy_{name}"
    return res_name, hcl_resource("alteon_http2_policy", res_name, attrs)


def cli_command_to_hcl(block: Block, used: set[str]) -> list[str]:
    name = unique_name(block.path.replace("/c/", "cli_"), used)
    return hcl_resource("alteon_cli_command", name, {"agalteonclicommand": cli_line(block)})


def blocks_to_terraform(blocks: Iterable[Block], native: bool = True) -> str:
    blocks = list(blocks)
    out: list[str] = [
        "terraform {",
        "  required_providers {",
        "    alteon = {",
        '      source = "Radware/alteon"',
        "    }",
        "  }",
        "}",
        "",
    ]

    used_cli_names: set[str] = set()

    service_data = merge_service_blocks(blocks)
    real_layer7_data = merge_real_server_layer7_blocks(blocks)
    filter_data = merge_filter_blocks(blocks)
    ssl_policy_data = merge_ssl_policy_blocks(blocks)
    ssl_cert_data = merge_ssl_cert_blocks(blocks)
    ssl_cert_group_data = merge_ssl_cert_group_blocks(blocks)
    http2_policy_data = merge_http2_policy_blocks(blocks)
    vrrp_data = merge_vrrp_blocks(blocks)
    vrrp_group_data = merge_vrrp_group_blocks(blocks)
    pip_data = merge_pip_blocks(blocks)
    data_class_data = merge_data_class_blocks(blocks)
    content_class_data = merge_content_class_blocks(blocks)
    appshape_script_data = merge_appshape_script_blocks(blocks)
    appshape_binding_data = merge_appshape_binding_blocks(blocks, service_data)
    advhc_data = merge_advhc_blocks(blocks)

    # Pre-render services grouped by virtual server ID.
    services_by_virt: dict[str, list[tuple[tuple[str, int, str | None], list[str]]]] = {}
    if native:
        for key, data in sorted(
            service_data.items(),
            key=lambda item: (item[1]["virt_id"], int(item[1].get("service_index") or 0)),
        ):
            _, lines = service_to_hcl(data)
            services_by_virt.setdefault(data["virt_id"], []).append((key, lines))

    emitted_service_keys: set[tuple[str, int, str | None]] = set()
    emitted_real_layer7: set[str] = set()
    emitted_filters: set[str] = set()
    emitted_ssl_policies = False
    emitted_ssl_certs = False
    emitted_ssl_cert_groups = False
    emitted_http2_policies = False
    emitted_pips = False
    emitted_data_classes = False
    emitted_content_classes = False
    emitted_appshape_scripts = False
    emitted_appshape_bindings = False
    emitted_advhc = False

    # 1) Policy resources first.
    if native:
        for name in sorted(ssl_policy_data):
            _, lines = ssl_policy_to_hcl(name, ssl_policy_data[name])
            out.extend(lines)
            out.append("")
        emitted_ssl_policies = True

        for cert_id, cert_type in sorted(ssl_cert_data):
            _, lines = ssl_cert_to_hcl(cert_id, cert_type, ssl_cert_data[(cert_id, cert_type)])
            out.extend(lines)
            out.append("")
        emitted_ssl_certs = True

        for group_id in sorted(ssl_cert_group_data):
            _, lines = ssl_cert_group_to_hcl(group_id, ssl_cert_group_data[group_id])
            out.extend(lines)
            out.append("")
        emitted_ssl_cert_groups = True

        for name in sorted(http2_policy_data):
            _, lines = http2_policy_to_hcl(name, http2_policy_data[name])
            out.extend(lines)
            out.append("")
        emitted_http2_policies = True

    # 2) Non-virtual resources in source order.
    for block in blocks:
        service_header = parse_service_header(block.path)
        if service_header and not is_appshape_binding_path(block.path):
            continue

        if is_ssl_policy_path(block.path):
            if native and emitted_ssl_policies:
                continue
        if is_ssl_cert_path(block.path):
            if native and emitted_ssl_certs:
                continue
        if is_ssl_cert_group_path(block.path):
            if native and emitted_ssl_cert_groups:
                continue
        if is_http2_policy_path(block.path):
            if native and emitted_http2_policies:
                continue

        if native and (is_vrrp_subpath(block.path) or is_vrrp_group_subpath(block.path)):
            # VRRP subcontexts are merged into their parent native resource.
            continue

        if native and is_real_layer7_path(block.path):
            index = path_id(r"/c/slb/real\s+(\S+)/layer7", block.path)
            if index and index in real_layer7_data and index not in emitted_real_layer7:
                _, lines = real_server_layer7_to_hcl(index, real_layer7_data[index])
                out.extend(lines)
                out.append("")
                emitted_real_layer7.add(index)
            continue

        if native and is_advhc_health_path(block.path):
            if not emitted_advhc:
                for name in sorted(advhc_data):
                    rendered_advhc = advhc_to_hcl(name, advhc_data[name])
                    if rendered_advhc:
                        _, lines = rendered_advhc
                        out.extend(lines)
                        out.append("")
                    else:
                        for raw_block in advhc_data[name]["raw"]:
                            out.extend(cli_command_to_hcl(raw_block, used_cli_names))
                            out.append("")
                emitted_advhc = True
            continue

        if native and is_pip_path(block.path):
            if not emitted_pips:
                for address in sorted(pip_data):
                    _, lines = pip_to_hcl(address, pip_data[address])
                    out.extend(lines)
                    out.append("")
                emitted_pips = True
            continue

        if native and is_data_class_path(block.path):
            if not emitted_data_classes:
                for dc_id in sorted(data_class_data):
                    _, lines = data_class_to_hcl(dc_id, data_class_data[dc_id])
                    out.extend(lines)
                    out.append("")
                emitted_data_classes = True
            continue

        if native and is_content_class_path(block.path):
            if not emitted_content_classes:
                for cc_id in sorted(content_class_data):
                    _, lines = content_class_to_hcl(cc_id, content_class_data[cc_id])
                    out.extend(lines)
                    out.append("")
                emitted_content_classes = True
            continue

        if native and is_appshape_script_path(block.path):
            if not emitted_appshape_scripts:
                for index in sorted(appshape_script_data):
                    _, lines = appshape_script_to_hcl(index, appshape_script_data[index])
                    out.extend(lines)
                    out.append("")
                emitted_appshape_scripts = True
            continue

        if native and is_appshape_binding_path(block.path):
            if not emitted_appshape_bindings:
                for key in sorted(appshape_binding_data):
                    _, lines = appshape_binding_to_hcl(key, appshape_binding_data[key])
                    out.extend(lines)
                    out.append("")
                emitted_appshape_bindings = True
            continue

        if native and (is_filter_path(block.path) or is_filter_subpath(block.path)):
            index = path_id(r"/c/slb/filt\s+(\d+)", block.path)
            if index and index in filter_data and index not in emitted_filters:
                _, lines = filter_to_hcl(index, filter_data[index])
                out.extend(lines)
                out.append("")
                emitted_filters.add(index)
            continue

        # Virtual servers are handled in the next pass so services can be placed
        # directly below their parent virtual server.
        if is_virt_path(block.path):
            continue

        rendered: tuple[str, list[str]] | None = None

        if native and is_real_path(block.path):
            rendered = block_to_real_server(block)
        elif native and is_group_path(block.path):
            rendered = block_to_server_group(block)
        elif native and is_vrrp_path(block.path):
            index = path_id(r"/c/l3/vrrp/vr\s+([^/\s]+)", block.path)
            if index and index in vrrp_data:
                rendered = vrrp_to_hcl(index, vrrp_data[index])
        elif native and is_vrrp_group_path(block.path):
            index = path_id(r"/c/l3/vrrp/(?:vrgroup|group)\s+([^/\s]+)", block.path)
            if index and index in vrrp_group_data:
                rendered = vrrp_group_to_hcl(index, vrrp_group_data[index])

        if rendered:
            _, lines = rendered
            out.extend(lines)
            out.append("")
        elif is_cli_supported_path(block.path) or (
            not native and (
                is_real_path(block.path)
                or is_real_layer7_path(block.path)
                or is_group_path(block.path)
                or is_filter_path(block.path)
                or is_vrrp_path(block.path)
                or is_vrrp_group_path(block.path)
                or is_ssl_cert_path(block.path)
                or is_ssl_cert_group_path(block.path)
                or is_pip_path(block.path)
                or is_advhc_health_path(block.path)
                or is_data_class_path(block.path)
                or is_content_class_path(block.path)
                or is_appshape_script_path(block.path)
                or is_appshape_binding_path(block.path)
            )
        ):
            out.extend(cli_command_to_hcl(block, used_cli_names))
            out.append("")

    # 3) Virtual servers directly followed by their services.
    for block in blocks:
        if not is_virt_path(block.path):
            continue

        if native:
            rendered = block_to_virtual_server(block)
            if rendered:
                _, lines = rendered
                out.extend(lines)
                out.append("")
        else:
            out.extend(cli_command_to_hcl(block, used_cli_names))
            out.append("")

        virt_id = path_id(r"/c/slb/virt\s+(\S+)", block.path)
        if not virt_id:
            continue

        if native:
            for key, lines in services_by_virt.get(virt_id, []):
                out.extend(lines)
                out.append("")
                emitted_service_keys.add(key)
        else:
            for service_block in blocks:
                parsed = parse_service_header(service_block.path)
                if parsed and parsed[0] == virt_id:
                    out.extend(cli_command_to_hcl(service_block, used_cli_names))
                    out.append("")

    # 4) Safety net for service blocks whose virtual server block is missing.
    if native:
        for key, data in sorted(
            service_data.items(),
            key=lambda item: (item[1]["virt_id"], int(item[1].get("service_index") or 0)),
        ):
            if key in emitted_service_keys:
                continue
            _, lines = service_to_hcl(data)
            out.extend(lines)
            out.append("")
    else:
        # In CLI-only mode, emit service blocks without a corresponding virtual
        # server block only once.
        known_virt_ids = {
            path_id(r"/c/slb/virt\s+(\S+)", b.path)
            for b in blocks
            if is_virt_path(b.path)
        }
        for block in blocks:
            parsed = parse_service_header(block.path)
            if parsed and parsed[0] not in known_virt_ids:
                out.extend(cli_command_to_hcl(block, used_cli_names))
                out.append("")

    return "\n".join(out).rstrip() + "\n"


def collect_imports(blocks: Iterable[Block], native: bool = True) -> list[dict[str, str]]:
    if not native:
        return []

    blocks = list(blocks)
    imports: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(resource: str, import_id: str) -> None:
        key = (resource, import_id)
        if key not in seen:
            imports.append({"resource": resource, "id": import_id})
            seen.add(key)

    service_data = merge_service_blocks(blocks)
    real_layer7_data = merge_real_server_layer7_blocks(blocks)
    pip_data = merge_pip_blocks(blocks)
    data_class_data = merge_data_class_blocks(blocks)
    content_class_data = merge_content_class_blocks(blocks)
    appshape_script_data = merge_appshape_script_blocks(blocks)
    appshape_binding_data = merge_appshape_binding_blocks(blocks, service_data)
    advhc_data = merge_advhc_blocks(blocks)
    ssl_cert_data = merge_ssl_cert_blocks(blocks)
    ssl_cert_group_data = merge_ssl_cert_group_blocks(blocks)

    for block in blocks:
        if is_real_path(block.path):
            index = path_id(r"/c/slb/real\s+(\S+)", block.path)
            parsed = parse_commands(block.commands)
            if index and (one_value(parsed, "rip") or one_value(parsed, "ipaddr")):
                add(f"alteon_real_server.{safe_name(f'real_server_{index}')}", index)

        elif is_group_path(block.path):
            index = path_id(r"/c/slb/group\s+(\S+)", block.path)
            if index:
                add(f"alteon_server_group.{safe_name(f'server_group_{index}')}", index)

        elif is_real_layer7_path(block.path):
            for index in sorted(real_layer7_data):
                add(f"alteon_real_server_layer7.{safe_name(f'real_server_layer7_{index}')}", index)

        elif is_filter_path(block.path) or is_filter_subpath(block.path):
            index = path_id(r"/c/slb/filt\s+(\d+)", block.path)
            if index:
                add(f"alteon_filter.{safe_name(f'filter_{index}')}", index)

        elif is_vrrp_path(block.path) or is_vrrp_subpath(block.path):
            index = path_id(r"/c/l3/vrrp/vr\s+([^/\s]+)", block.path)
            if index:
                add(f"alteon_vrrp.{safe_name(f'vrrp_{index}')}", index)

        elif is_vrrp_group_path(block.path) or is_vrrp_group_subpath(block.path):
            index = path_id(r"/c/l3/vrrp/(?:vrgroup|group)\s+([^/\s]+)", block.path)
            if index:
                add(f"alteon_vrrp_group.{safe_name(f'vrrp_group_{index}')}", index)

        elif is_pip_path(block.path):
            for address in sorted(pip_data):
                add(f"alteon_pip.{safe_name(f'pip_{address}')}", address)

        elif is_advhc_health_path(block.path):
            for name in sorted(advhc_data):
                hc_type = advhc_data[name].get("type")
                if hc_type:
                    add(f"alteon_advhc_{hc_type}.{safe_name(f'advhc_{hc_type}_{name}')}", name)

        elif is_data_class_path(block.path):
            for dc_id in sorted(data_class_data):
                add(f"alteon_data_class.{safe_name(f'data_class_{dc_id}')}", dc_id)

        elif is_content_class_path(block.path):
            for cc_id in sorted(content_class_data):
                add(f"alteon_content_class.{safe_name(f'content_class_{cc_id}')}", cc_id)

        elif is_appshape_script_path(block.path):
            for index in sorted(appshape_script_data):
                add(f"alteon_appshape_script.{safe_name(f'appshape_script_{index}')}", index)

        elif is_appshape_binding_path(block.path):
            for key, attrs in sorted(appshape_binding_data.items()):
                if attrs["target"] == "filter":
                    import_id = f"filter:{attrs['filter']}/{attrs['priority']}"
                else:
                    import_id = f"service:{attrs['virtual_server']}/{attrs['virtual_service']}/{attrs['priority']}"
                add(f"alteon_appshape_binding.{safe_name(f'appshape_binding_{key}')}", import_id)

        elif is_virt_path(block.path):
            index = path_id(r"/c/slb/virt\s+(\S+)", block.path)
            parsed = parse_commands(block.commands)
            if index and one_value(parsed, "vip"):
                add(f"alteon_virtual_server.{safe_name(f'virtual_server_{index}')}", index)

        elif is_ssl_policy_path(block.path):
            m = re.fullmatch(r"/c/slb/ssl/sslpol\s+([^/\s]+)(?:/.+)?", block.path)
            if m:
                name = m.group(1)
                add(f"alteon_ssl_policy.{safe_name(f'ssl_policy_{name}')}", name)

        elif is_ssl_cert_path(block.path):
            for cert_id, cert_type in sorted(ssl_cert_data):
                add(
                    f"alteon_ssl_cert.{safe_name(f'ssl_cert_{cert_id}_{cert_type}')}",
                    f"{cert_id}/{cert_type}",
                )

        elif is_ssl_cert_group_path(block.path):
            for group_id in sorted(ssl_cert_group_data):
                add(f"alteon_ssl_cert_group.{safe_name(f'ssl_cert_group_{group_id}')}", group_id)

        elif is_http2_policy_path(block.path):
            m = re.fullmatch(r"/c/slb/(?:accel/)?http2/(?:pol|policy)\s+(\S+)(?:/.+)?", block.path)
            if not m:
                m = re.fullmatch(r"/c/slb/http2pol\s+(\S+)(?:/.+)?", block.path)
            if m:
                name = m.group(1)
                add(f"alteon_http2_policy.{safe_name(f'http2_policy_{name}')}", name)

    # New flat virtual_service has two keys:
    #   servindex = virtual server index
    #   index     = ordinal service index on that virtual server, not the port.
    for _, data in sorted(service_data.items(), key=lambda item: (item[1]["virt_id"], int(item[1].get("service_index") or 0))):
        virt_id = data["virt_id"]
        port = data["port"]
        proto = data["protocol"] or "ip"
        service_index = int(data.get("service_index") or 1)
        add(
            f"alteon_virtual_service.{safe_name(f'virtual_service_{virt_id}_{port}_{proto}')}",
            f"{virt_id}/{service_index}",
        )

    return imports


def imports_to_terraform(imports: Iterable[dict[str, str]]) -> str:
    lines: list[str] = []
    for item in imports:
        lines.extend([
            "import {",
            f"  to = {item['resource']}",
            f"  id = {hcl_value(item['id'])}",
            "}",
            "",
        ])
    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def write_import_file(imports: Iterable[dict[str, str]], filename: str | Path) -> None:
    Path(filename).write_text(imports_to_terraform(imports), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Konvertiert Alteon-SLB-Konfigurationsdump in Terraform.")
    parser.add_argument("input", type=Path, help="Alteon-Konfigurationsdump")
    parser.add_argument("-o", "--output", type=Path, default=Path("main.tf"), help="Zieldatei, Default: main.tf")
    parser.add_argument("-i", "--import-file", help="Generate Terraform import blocks")
    parser.add_argument("--cli-only", action="store_true", help="Auch Flat-Resources als alteon_cli_command ausgeben.")
    args = parser.parse_args()

    print(f"Alteon Configuration Converter v{__version__} (c) 2026 Michael Schwenke")

    text = args.input.read_text(encoding="utf-8", errors="replace")
    blocks = parse_alteon_config(text)
    native = not args.cli_only

    hcl = blocks_to_terraform(blocks, native=native)
    args.output.write_text(hcl, encoding="utf-8")

    generated_imports = collect_imports(blocks, native=native)
    if args.import_file:
        write_import_file(generated_imports, args.import_file)

    relevant = [
        b for b in blocks
        if is_real_path(b.path)
        or is_real_layer7_path(b.path)
        or is_group_path(b.path)
        or is_filter_path(b.path)
        or is_filter_subpath(b.path)
        or is_virt_path(b.path)
        or is_virt_service_path(b.path)
        or is_ssl_policy_path(b.path)
        or is_ssl_cert_path(b.path)
        or is_ssl_cert_group_path(b.path)
        or is_http2_policy_path(b.path)
        or is_pip_path(b.path)
        or is_data_class_path(b.path)
        or is_content_class_path(b.path)
        or is_appshape_script_path(b.path)
        or is_appshape_binding_path(b.path)
        or is_vrrp_path(b.path)
        or is_vrrp_group_path(b.path)
        or is_vrrp_subpath(b.path)
        or is_vrrp_group_subpath(b.path)
        or is_cli_supported_path(b.path)
    ]

    print(f"alteon_to_terraform {__version__}")
    print(f"OK: {len(relevant)} relevante Alteon-Blöcke nach {args.output} geschrieben.")
    if args.import_file:
        print(f"OK: {len(generated_imports)} Import-Blöcke nach {args.import_file} geschrieben.")
    print("Modus:", "Flat Native Resources" if native else "CLI only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
