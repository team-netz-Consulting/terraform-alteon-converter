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
# - /c/slb/group
# - /c/slb/virt
# - /c/slb/virt/service
# - /c/slb/ssl/sslpol
# - /c/slb/ssl/certs/group
# - /c/slb/advhc/health
# - /c/slb/filt
# - /c/l3/vrrp/vr
# - /c/l3/vrrp/vrgroup
#
# Generated Terraform Resources:
# - alteon_real_server
# - alteon_server_group
# - alteon_virtual_server
# - alteon_virtual_service
# - alteon_ssl_policy
# - alteon_http2_policy
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
# 0.4.5
#
# Release Date:
# 2026-06-17
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
alteon_to_terraform_flat_v4_5.py
Version: 0.4.5

Converts selected Radware Alteon configuration sections into
Terraform resources for the Alteon Terraform Provider.

Currently supported:

Native Resources:
- /c/slb/real                    -> alteon_real_server
- /c/slb/group                   -> alteon_server_group
- /c/slb/virt                    -> alteon_virtual_server
- /c/slb/virt/service            -> alteon_virtual_service
- /c/slb/ssl/sslpol             -> alteon_ssl_policy
- /c/slb/http2/*                -> alteon_http2_policy
- /c/l3/vrrp/vr                  -> alteon_vrrp
- /c/l3/vrrp/vrgroup             -> alteon_vrrp_group

CLI Fallback Resources:
- /c/slb/filt
- /c/slb/advhc/health
- /c/slb/ssl/certs/group

Import generation:
- alteon_real_server
- alteon_server_group
- alteon_virtual_server
- alteon_virtual_service
- alteon_ssl_policy
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
    Server Group     -> <index>
    Virtual Server   -> <index>
    SSL Policy       -> <name>
    Virtual Service  -> <virt_id>/<service_index>
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
__version__ = "0.4.5"
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

        if stripped.startswith("/*") or stripped.startswith("script "):
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
    return bool(re.fullmatch(r"/c/slb/real\s+\S+", path))


def is_real_subpath(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/real\s+\S+/.+", path))


def is_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/group\s+\S+", path))


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


def is_advhc_health_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/advhc/health\s+\S+(?:\s+\S+)?(?:/.+)?", path))


def is_ssl_cert_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/ssl/certs/group\s+\S+", path))


def is_cli_supported_path(path: str) -> bool:
    return bool(
        is_ssl_cert_group_path(path)
        or is_advhc_health_path(path)
        or re.fullmatch(r"/c/slb/filt\s+\S+(?:/.+)?", path)
        or is_real_subpath(path)
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
            # Unknown VRRP subcontexts are intentionally ignored by native mapping.
            pass
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
            pass
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
    res_name = f"vrrp_group_{index}"
    return res_name, hcl_resource("alteon_vrrp_group", res_name, attrs)



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
    value = clean_quote(value)
    if not value:
        return None
    # Conservative mapping. Unknown values are skipped instead of producing
    # invalid integers for the flat provider.
    mapping = {
        "disable": 1,
        "disabled": 1,
        "off": 1,
        "forceproxy": 2,
        "force-proxy": 2,
        "enable": 2,
        "enabled": 2,
        "on": 2,
    }
    return mapping.get(value.lower())


def service_to_hcl(data: dict[str, Any]) -> tuple[str, list[str]]:
    virt_id = data["virt_id"]
    port = data["port"]
    proto = data["protocol"]

    parsed = parse_commands(data["base"])
    parsed_ssl = parse_commands(data["ssl"])
    parsed_http = parse_commands(data["http"])

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
    xff = enum_enable(one_value(parsed_http, "xforward"))
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
            attrs["serv_cert_grp_mark"] = 1
        elif len(parts) >= 2 and parts[0].lower() == "cert":
            attrs["serv_cert"] = parts[-1]
            attrs["serv_cert_grp_mark"] = 0
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


def parse_cipher_command(value: str | None) -> tuple[str | None, str | None]:
    value = clean_quote(value)
    if not value:
        return None, None
    parts = split_cmd(value)
    if len(parts) >= 2 and parts[0].lower() in {"user-defined", "userdefined"}:
        return "user-defined", parts[1]
    return parts[0] if parts else value, None


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
        attrs["admin_status"] = 2
    elif "dis" in main:
        attrs["admin_status"] = 3

    convert = enum_enable(one_value(main, "convert"))
    if convert is not None:
        attrs["convert"] = convert

    fessl = enum_enable(one_value(main, "fessl"))
    if fessl is not None:
        attrs["fessl"] = fessl

    cipher_raw = one_value(main, "cipher")
    cipher_name, cipher_userdef = parse_cipher_command(cipher_raw)
    if cipher_userdef:
        attrs["cipher_userdef"] = cipher_userdef
    elif cipher_name and cipher_name.isdigit():
        attrs["cipher_name"] = int(cipher_name)

    intermca = clean_quote(one_value(main, "intermca"))
    if intermca:
        parts = split_cmd(intermca)
        if len(parts) >= 2:
            attrs["intermca_chain_type"] = parts[0]
            attrs["intermca_chain_name"] = parts[1]

    secreneg = clean_quote(one_value(main, "secreneg"))
    if secreneg:
        attrs["secreneg"] = secreneg

    be_ssl = enum_enable(one_value(backend, "ssl"))
    if be_ssl is not None:
        attrs["bessl"] = be_ssl

    be_cipher_raw = one_value(backend, "cipher")
    be_cipher_name, be_cipher_userdef = parse_cipher_command(be_cipher_raw)
    if be_cipher_userdef:
        attrs["be_cipher_userdef"] = be_cipher_userdef
    elif be_cipher_name and be_cipher_name.isdigit():
        attrs["becipher"] = int(be_cipher_name)

    pass_frontend = enum_enable(one_value(passinfo, "frontend"))
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
        value = enum_enable(one_value(frver, key))
        if value is not None:
            attrs[tf_key] = value

    for key, tf_key in {
        "tls10": "be_tls10_version",
        "tls11": "be_tls11_version",
        "tls12": "be_tls12_version",
        "tls13": "be_tls13_version",
        "sslv3": "be_sslv3_version",
    }.items():
        value = enum_enable(one_value(bever, key))
        if value is not None:
            attrs[tf_key] = value

    res_name = f"ssl_policy_{name}"
    return res_name, hcl_resource("alteon_ssl_policy", res_name, attrs)


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
    ssl_policy_data = merge_ssl_policy_blocks(blocks)
    http2_policy_data = merge_http2_policy_blocks(blocks)
    vrrp_data = merge_vrrp_blocks(blocks)
    vrrp_group_data = merge_vrrp_group_blocks(blocks)

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
    emitted_ssl_policies = False
    emitted_http2_policies = False

    # 1) Policy resources first.
    if native:
        for name in sorted(ssl_policy_data):
            _, lines = ssl_policy_to_hcl(name, ssl_policy_data[name])
            out.extend(lines)
            out.append("")
        emitted_ssl_policies = True

        for name in sorted(http2_policy_data):
            _, lines = http2_policy_to_hcl(name, http2_policy_data[name])
            out.extend(lines)
            out.append("")
        emitted_http2_policies = True

    # 2) Non-virtual resources in source order.
    for block in blocks:
        service_header = parse_service_header(block.path)
        if service_header:
            continue

        if is_ssl_policy_path(block.path):
            if native and emitted_ssl_policies:
                continue
        if is_http2_policy_path(block.path):
            if native and emitted_http2_policies:
                continue

        if is_vrrp_subpath(block.path) or is_vrrp_group_subpath(block.path):
            # Track subcontexts are merged into their parent native resource.
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
            not native and (is_real_path(block.path) or is_group_path(block.path) or is_vrrp_path(block.path) or is_vrrp_group_path(block.path))
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

    imports: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(resource: str, import_id: str) -> None:
        key = (resource, import_id)
        if key not in seen:
            imports.append({"resource": resource, "id": import_id})
            seen.add(key)

    service_data = merge_service_blocks(list(blocks))
    blocks = list(blocks)

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

        elif is_vrrp_path(block.path):
            index = path_id(r"/c/l3/vrrp/vr\s+([^/\s]+)", block.path)
            if index:
                add(f"alteon_vrrp.{safe_name(f'vrrp_{index}')}", index)

        elif is_vrrp_group_path(block.path):
            index = path_id(r"/c/l3/vrrp/(?:vrgroup|group)\s+([^/\s]+)", block.path)
            if index:
                add(f"alteon_vrrp_group.{safe_name(f'vrrp_group_{index}')}", index)

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
        or is_group_path(b.path)
        or is_virt_path(b.path)
        or is_virt_service_path(b.path)
        or is_ssl_policy_path(b.path)
        or is_http2_policy_path(b.path)
        or is_vrrp_path(b.path)
        or is_vrrp_group_path(b.path)
        or is_vrrp_subpath(b.path)
        or is_vrrp_group_subpath(b.path)
        or is_cli_supported_path(b.path)
    ]

    print("alteon_to_terraform_flat_v4_5")
    print(f"OK: {len(relevant)} relevante Alteon-Blöcke nach {args.output} geschrieben.")
    if args.import_file:
        print(f"OK: {len(generated_imports)} Import-Blöcke nach {args.import_file} geschrieben.")
    print("Modus:", "Flat Native Resources" if native else "CLI only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())