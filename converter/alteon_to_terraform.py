#!/usr/bin/env python3
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
# using the official Radware Alteon Terraform Provider.
#
# Supported Objects:
# - /c/slb/real
# - /c/slb/group
# - /c/slb/virt
# - /c/slb/virt/service
# - /c/slb/ssl/certs/group
# - /c/slb/filt
#
# Generated Terraform Resources:
# - alteon_real_server
# - alteon_server_group
# - alteon_virtual_server
# - alteon_virtual_service
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
# 0.3.2
#
# Release Date:
# 2026-06-11
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
# Copyright 2026 Michael Schwenke
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
# 0.3.3
# - Add schema for real Server
#
# 0.3.2
# - Added Terraform import file generation with -i/--import-file
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

'''
alteon_to_terraform_native_v3_3.py
Version: native-v3.3

Konvertiert ausgewählte Alteon-CLI-Dump-Blöcke in Terraform
für den Radware/alteon Provider.

Aktuell:
  - /c/slb/real <id>                 -> alteon_real_server
  - /c/slb/virt <id>                 -> alteon_virtual_server, alle IDs
  - /c/slb/virt <id>/service ...     -> alteon_virtual_service, alle IDs
  - /c/slb/group <id>                -> alteon_server_group
  - /c/slb/filt <id>                 -> alteon_cli_command
  - /c/slb/filt <id>/...             -> alteon_cli_command
  - /c/slb/ssl/certs/group <id>      -> alteon_cli_command

Bewusst nicht übernommen:
  - Private Keys, Zertifikats-Payloads, Requests
  - Nicht genannte Alteon-Kontexte

Hinweis:
  Der Provider arbeitet teilweise mit numerischen Enum-Werten.
  Die wichtigsten Werte werden hier pragmatisch gemappt:
    ena/enabled/e -> 1
    dis/disabled/d -> 2
    ipver v4 -> 4
    ipver v6 -> 6
'''

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

__author__ = "Michael Schwenke"
__company__ = "Team-Netz GmbH"
__version__ = "0.3.3"
__license__ = "Apache-2.0"
__status__ = "Development"


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


def is_cli_supported_path(path: str) -> bool:
    return bool(
        re.fullmatch(r"/c/slb/ssl/certs/group\s+\S+", path)
        or re.fullmatch(r"/c/slb/filt\s+\S+(?:/.+)?", path)
    )


def is_group_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/group\s+\S+", path))


def is_real_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/real\s+\S+", path))


def is_virt_path(path: str) -> bool:
    return bool(re.fullmatch(r"/c/slb/virt\s+\S+", path))


def is_virt_service_path(path: str) -> bool:
    return bool(parse_service_header(path))


def is_virt_service_ssl_path(path: str) -> bool:
    parsed = parse_service_header(path)
    return bool(parsed and parsed[3])


def parse_commands(commands: list[str]) -> dict[str, list[str]]:
    parsed: dict[str, list[str]] = {}
    for cmd in commands:
        parts = cmd.split()
        if not parts:
            continue
        parsed.setdefault(parts[0], []).append(" ".join(parts[1:]))
    return parsed


def one_value(parsed: dict[str, list[str]], key: str) -> str | None:
    values = parsed.get(key)
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


def enum_enable(value: str) -> int:
    v = value.lower()
    if v in {"ena", "enabled", "enable", "e", "on"}:
        return 1
    if v in {"dis", "disabled", "disable", "d", "off"}:
        return 2
    raise ValueError(f"Unbekannter Enable/Disable-Wert: {value}")


def ipver_to_number(value: str | None) -> int | None:
    if value is None:
        return None
    v = value.lower().strip()
    if v == "v4":
        return 4
    if v == "v6":
        return 6
    return None


def hcl_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) or isinstance(value, float):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def hcl_block(name: str, attrs: dict[str, Any], indent: int = 2) -> list[str]:
    pad = " " * indent
    lines = [f"{pad}{name} {{"]
    for key, value in attrs.items():
        if value is None:
            continue
        lines.append(f"{pad}  {key} = {hcl_value(value)}")
    lines.append(f"{pad}}}")
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


def block_to_real_server(block: Block) -> tuple[str, list[str]] | None:
    m = re.fullmatch(r"/c/slb/real\s+(\S+)", block.path)
    if not m:
        return None

    index = m.group(1)
    parsed = parse_commands(block.commands)

    ipaddr = one_value(parsed, "rip") or one_value(parsed, "ipaddr")
    if not ipaddr:
        return None

    attrs: dict[str, Any] = {
        "ipaddr": ipaddr,
        "ipver": ipver_to_number(one_value(parsed, "ipver")),
        "name": clean_quote(one_value(parsed, "name")),
    }

    if "ena" in parsed:
        attrs["state"] = 1
    elif "dis" in parsed:
        attrs["state"] = 2

    # Direkt abbildbare String-Felder aus dem Provider-Schema.
    direct_string_keys = {
        "ipv6addr": "ipv6addr",
        "copy": "copy",
        "portsingress": "portsingress",
        "portsegress": "portsegress",
        "urlbmap": "urlbmap",
        "proxyipaddress": "proxyipaddress",
        "proxyipaddr": "proxyipaddress",
        "proxyipmask": "proxyipmask",
        "proxyipv6address": "proxyipv6address",
        "proxyipv6addr": "proxyipv6address",
        "proxyipnwclass": "proxyipnwclass",
        "oid": "oid",
        "commstring": "commstring",
        "backup": "backup",
        "healthid": "healthid",
        "hcid": "healthid",
    }

    # Integer-Felder aus dem Provider-Schema. Werte können je nach Alteon-CLI
    # numerisch oder als ena/dis geschrieben sein; beides wird behandelt.
    direct_int_keys = {
        "weight": "weight",
        "maxconns": "maxconns",
        "maxconn": "maxconns",
        "timeout": "timeout",
        "pinginterval": "pinginterval",
        "pingint": "pinginterval",
        "failretry": "failretry",
        "succretry": "succretry",
        "deletestatus": "deletestatus",
        "type": "type",
        "addurl": "addurl",
        "remurl": "remurl",
        "cookie": "cookie",
        "excludestr": "excludestr",
        "submac": "submac",
        "idsport": "idsport",
        "nxtrportidx": "nxtrportidx",
        "nxtbuddyidx": "nxtbuddyidx",
        "llbtype": "llbtype",
        "addportsingress": "addportsingress",
        "remportsingress": "remportsingress",
        "addportsegress": "addportsegress",
        "remportsegress": "remportsegress",
        "vlaningress": "vlaningress",
        "vlanegress": "vlanegress",
        "egressif": "egressif",
        "sectype": "sectype",
        "ingressif": "ingressif",
        "secdeviceflag": "secdeviceflag",
        "ingport": "ingport",
        "proxy": "proxy",
        "ldapwr": "ldapwr",
        "idsvlan": "idsvlan",
        "avail": "avail",
        "fasthealthcheck": "fasthealthcheck",
        "subdmac": "subdmac",
        "overflow": "overflow",
        "bkppreempt": "bkppreempt",
        "mode": "mode",
        "updateallrealservers": "updateallrealservers",
        "proxyipmode": "proxyipmode",
        "proxyipv6prefix": "proxyipv6prefix",
        "proxyippersistency": "proxyippersistency",
        "proxyipnwclasspersistency": "proxyipnwclasspersistency",
        "ingvlan": "ingvlan",
        "criticalconnthrsh": "criticalconnthrsh",
        "highconnthrsh": "highconnthrsh",
        "uploadbandwidth": "uploadbandwidth",
        "downloadbandwidth": "downloadbandwidth",
    }

    for cli_key, tf_key in direct_string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            attrs[tf_key] = value

    for cli_key, tf_key in direct_int_keys.items():
        value = one_value(parsed, cli_key)
        if not value:
            continue
        value = clean_quote(value) or value
        if re.fullmatch(r"-?\d+", value):
            attrs[tf_key] = int(value)
        else:
            try:
                attrs[tf_key] = enum_enable(value)
            except ValueError:
                # Unbekannte Text-Enums werden bewusst ausgelassen, damit die
                # erzeugte HCL nicht mit falschem Typ invalid wird.
                pass

    name = f"real_server_{index}"
    lines = [
        f'resource "alteon_real_server" "{safe_name(name)}" {{',
        f'  index = {hcl_value(index)}',
        *hcl_block("elements", attrs, indent=2),
        "}",
    ]
    return name, lines


def block_to_server_group(block: Block) -> tuple[str, list[str]] | None:
    m = re.fullmatch(r"/c/slb/group\s+(\S+)", block.path)
    if not m:
        return None

    index = m.group(1)
    parsed = parse_commands(block.commands)

    base_attrs: dict[str, Any] = {
        "ipver": ipver_to_number(one_value(parsed, "ipver")),
        "name": clean_quote(one_value(parsed, "name")),
    }

    # Häufige Alteon-CLI-Kommandos, soweit sie direkt zu Provider-Feldern passen.
    direct_string_keys = {
        "backup": "backup",
        "backupgroup": "backupgroup",
        "backupserver": "backupserver",
        "healthid": "healthid",
        "hcid": "healthid",
        "healthcheckurl": "healthcheckurl",
        "phashmask": "phashmask",
    }
    direct_int_keys = {
        "metric": "metric",
        "realthreshold": "realthreshold",
        "viphealthcheck": "viphealthcheck",
        "idsstate": "idsstate",
        "idsport": "idsport",
        "idsflood": "idsflood",
        "minmisshash": "minmisshash",
        "rmetric": "rmetric",
        "operatoraccess": "operatoraccess",
        "wlm": "wlm",
        "slowstart": "slowstart",
        "minthreshold": "minthreshold",
        "maxthreshold": "maxthreshold",
        "backuptype": "backuptype",
        "phashprefixlength": "phashprefixlength",
        "type": "type",
        "idschain": "idschain",
        "sectype": "sectype",
        "secdeviceflag": "secdeviceflag",
        "maxconex": "maxconex",
    }

    for cli_key, tf_key in direct_string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            base_attrs[tf_key] = value

    for cli_key, tf_key in direct_int_keys.items():
        value = one_value(parsed, cli_key)
        if value and re.fullmatch(r"-?\d+", value):
            base_attrs[tf_key] = int(value)

    add_servers = [clean_quote(v) for v in parsed.get("add", [])]
    add_servers = [v for v in add_servers if v]

    res_base = safe_name(f"server_group_{index}")
    lines: list[str] = []

    # Basis-Resource für die Gruppe selbst. Wenn außer addserver nichts vorhanden ist,
    # wird der erste addserver hier verwendet, damit elements nicht leer ist.
    base_elements = {k: v for k, v in base_attrs.items() if v is not None}
    first_add_in_base = False
    if not base_elements and add_servers:
        base_elements["addserver"] = add_servers[0]
        first_add_in_base = True

    if base_elements:
        lines.extend([
            f'resource "alteon_server_group" "{res_base}" {{',
            f'  index = {hcl_value(index)}',
            *hcl_block("elements", base_elements, indent=2),
            "}",
            "",
        ])

    remaining_servers = add_servers[1:] if first_add_in_base else add_servers
    previous_ref = f"alteon_server_group.{res_base}" if base_elements else None

    for server in remaining_servers:
        member_name = safe_name(f"server_group_{index}_add_{server}")
        lines.extend([
            f'resource "alteon_server_group" "{member_name}" {{',
            f'  index = {hcl_value(index)}',
        ])
        if previous_ref:
            lines.append(f"  depends_on = [{previous_ref}]")
        lines.extend(hcl_block("elements", {"addserver": server}, indent=2))
        lines.append("}")
        lines.append("")
        previous_ref = f"alteon_server_group.{member_name}"

    if not lines:
        return None

    while lines and lines[-1] == "":
        lines.pop()
    return f"server_group_{index}", lines

def block_to_virtual_server(block: Block) -> tuple[str, list[str]] | None:
    m = re.fullmatch(r"/c/slb/virt\s+(\S+)", block.path)
    if not m:
        return None

    index = m.group(1)
    parsed = parse_commands(block.commands)

    vip = one_value(parsed, "vip")
    if not vip:
        return None

    attrs: dict[str, Any] = {
        "virtserveripaddress": vip,
        "virtserveripver": ipver_to_number(one_value(parsed, "ipver")),
        "virtservervname": clean_quote(one_value(parsed, "name")),
    }

    if "ena" in parsed:
        attrs["virtserverstate"] = 1
    elif "dis" in parsed:
        attrs["virtserverstate"] = 2

    # Mapping gemäß alteon_virtual_server Schema.
    # Nur direkt erkennbare Alteon-CLI-Keys werden gesetzt.
    direct_string_keys = {
        "dname": "virtserverdname",
        "domain": "virtserverdname",
        "ipv6": "virtserveripv6addr",
        "ipv6addr": "virtserveripv6addr",
        "srcnetwork": "virtserversrcnetwork",
        "nat": "virtservernat",
        "nat6": "virtservernat6",
        "wanlink": "virtserverwanlink",
        "rule": "virtserverrule",
    }
    direct_int_keys = {
        "l3only": "virtserverlayer3only",
        "layer3only": "virtserverlayer3only",
        "bwmcontract": "virtserverbwmcontract",
        "weight": "virtserverweight",
        "avail": "virtserveravail",
        "addrule": "virtserveraddrule",
        "removerule": "virtserverremoverule",
        "freeserviceidx": "virtserverfreeserviceidx",
        "creset": "virtservercreset",
        "isdnssecvip": "virtserverisdnssecvip",
        "availpersist": "virtserveravailpersist",
        "rtsrcmac": "virtserverrtsrcmac",
        "creationtype": "virtservercreationtype",
    }

    for cli_key, tf_key in direct_string_keys.items():
        value = clean_quote(one_value(parsed, cli_key))
        if value:
            attrs[tf_key] = value

    for cli_key, tf_key in direct_int_keys.items():
        value = one_value(parsed, cli_key)
        if value and re.fullmatch(r"-?\d+", value):
            attrs[tf_key] = int(value)
        elif value:
            try:
                attrs[tf_key] = enum_enable(value)
            except ValueError:
                pass

    name = f"virtual_server_{index}"
    lines = [
        f'resource "alteon_virtual_server" "{safe_name(name)}" {{',
        f'  index = {hcl_value(index)}',
        *hcl_block("elements", attrs, indent=2),
        "}",
    ]
    return name, lines


def parse_service_header(path: str) -> tuple[str, int, str | None, bool] | None:
    # /c/slb/virt 1000/service 443 https[/ssl]
    # Protokoll darf nicht über den /ssl-Unterpfad hinaus greedy matchen.
    m = re.fullmatch(r"/c/slb/virt\s+(\S+)/service\s+(\d+)(?:\s+([^/]+))?(?:/ssl)?", path)
    if not m:
        return None
    virt_id = m.group(1)
    port = int(m.group(2))
    protocol = m.group(3).strip() if m.group(3) else None
    is_ssl = path.endswith("/ssl")
    return virt_id, port, protocol, is_ssl


def service_key(block: Block) -> tuple[str, int, str | None] | None:
    parsed = parse_service_header(block.path)
    if not parsed:
        return None
    virt_id, port, protocol, _ = parsed
    return virt_id, port, protocol


def merge_service_blocks(blocks: list[Block]) -> dict[tuple[str, int, str | None], dict[str, Any]]:
    services: dict[tuple[str, int, str | None], dict[str, Any]] = {}

    for block in blocks:
        parsed_header = parse_service_header(block.path)
        if not parsed_header:
            continue

        virt_id, port, protocol, is_ssl = parsed_header
        key = (virt_id, port, protocol)
        data = services.setdefault(
            key,
            {
                "virt_id": virt_id,
                "port": port,
                "protocol": protocol,
                "commands": [],
                "ssl_commands": [],
            },
        )

        if is_ssl:
            data["ssl_commands"].extend(block.commands)
        else:
            data["commands"].extend(block.commands)

    return services


def service_to_hcl(data: dict[str, Any]) -> tuple[str, list[str]]:
    virt_id = data["virt_id"]
    port = data["port"]
    protocol = data["protocol"]
    parsed = parse_commands(data["commands"])
    parsed_ssl = parse_commands(data["ssl_commands"])

    elements: dict[str, Any] = {
        "virtport": int(port),
    }

    rport = one_value(parsed, "rport")
    if rport and rport.isdigit():
        elements["realport"] = int(rport)

    # realgroup liegt laut Provider-Schema in elements_7.
    elements_7: dict[str, Any] = {}
    group = one_value(parsed, "group")
    if group:
        elements_7["realgroup"] = group

    elements_2: dict[str, Any] = {}
    srvrcert = one_value(parsed_ssl, "srvrcert")
    # Alteon CLI: srvrcert cert 1001 -> Provider: servcert = 1001
    if srvrcert:
        parts = srvrcert.split()
        elements_2["servcert"] = parts[-1] if parts else srvrcert
        if len(parts) >= 2 and parts[0] == "group":
            elements_5 = {"servcertgrpmark": 1}
        else:
            elements_5 = {"servcertgrpmark": 0}
    else:
        elements_5 = {}

    res_name = f"virtual_service_{virt_id}_{port}_{protocol or 'ip'}"
    lines = [
        f'resource "alteon_virtual_service" "{safe_name(res_name)}" {{',
        f"  index     = {int(port)}",
        f'  servindex = {hcl_value(virt_id)}',
        *hcl_block("elements", elements, indent=2),
    ]

    if elements_2:
        lines.extend(hcl_block("elements_2", elements_2, indent=2))
    if elements_5:
        lines.extend(hcl_block("elements_5", elements_5, indent=2))
    if elements_7:
        lines.extend(hcl_block("elements_7", elements_7, indent=2))

    lines.append("}")
    return res_name, lines


def cli_command_to_hcl(block: Block, used: set[str]) -> list[str]:
    name = unique_name(block.path.replace("/c/slb/", "cli_"), used)
    return [
        f'resource "alteon_cli_command" "{name}" {{',
        "  elements {",
        f"    agalteonclicommand = {hcl_value(cli_line(block))}",
        "  }",
        "}",
    ]


def blocks_to_terraform(blocks: Iterable[Block], native: bool = True) -> str:
    blocks = list(blocks)
    out: list[str] = [
        'terraform {',
        '  required_providers {',
        '    alteon = {',
        '      source = "Radware/alteon"',
        '    }',
        '  }',
        '}',
        '',
    ]

    used_cli_names: set[str] = set()
    native_resource_names: set[str] = set()

    service_data = merge_service_blocks(blocks)
    service_keys = set(service_data.keys())

    for block in blocks:
        # SSL-Service-Blöcke werden mit dem Basis-Service zusammengeführt.
        key = service_key(block)
        if key in service_keys:
            continue

        rendered: tuple[str, list[str]] | None = None

        if native and is_real_path(block.path):
            rendered = block_to_real_server(block)
        elif native and is_group_path(block.path):
            rendered = block_to_server_group(block)
        elif native and is_virt_path(block.path):
            rendered = block_to_virtual_server(block)

        if rendered:
            name, lines = rendered
            # Absicherung gegen doppelte Namen, falls IDs Sonderzeichen enthalten.
            unique_name(name, native_resource_names)
            out.extend(lines)
            out.append("")
        elif is_cli_supported_path(block.path) or (not native and is_group_path(block.path)):
            out.extend(cli_command_to_hcl(block, used_cli_names))
            out.append("")

    if native:
        for _, data in sorted(service_data.items(), key=lambda item: (item[1]["virt_id"], item[1]["port"], item[1]["protocol"] or "")):
            name, lines = service_to_hcl(data)
            unique_name(name, native_resource_names)
            out.extend(lines)
            out.append("")
    else:
        for block in blocks:
            if is_real_path(block.path) or is_group_path(block.path) or is_virt_path(block.path) or is_virt_service_path(block.path):
                out.extend(cli_command_to_hcl(block, used_cli_names))
                out.append("")

    return "\n".join(out).rstrip() + "\n"

def collect_imports(blocks: Iterable[Block], native: bool = True) -> list[dict[str, str]]:
    """
    Erzeugt Terraform import-Blöcke für Native-Resources.

    Aktuell werden bewusst nur die vom Benutzer gewünschten Basisobjekte
    importiert:
      - alteon_real_server
      - alteon_server_group
      - alteon_virtual_server

    Nicht importiert werden:
      - alteon_virtual_service, weil der Provider-Import-Key je nach Version
        unterschiedlich sein kann.
      - zusätzliche group addserver-Resources, da diese denselben Alteon-Index
        verwenden und nur Änderungsoperationen für Mitgliedschaften darstellen.
      - alteon_cli_command-Fallbacks.
    """
    if not native:
        return []

    imports: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for block in blocks:
        resource_type: str | None = None
        resource_name: str | None = None
        import_id: str | None = None

        if is_real_path(block.path):
            m = re.fullmatch(r"/c/slb/real\s+(\S+)", block.path)
            parsed = parse_commands(block.commands)
            # Nur importieren, wenn auch eine Native-Resource erzeugt wird.
            if m and one_value(parsed, "rip"):
                import_id = m.group(1)
                resource_type = "alteon_real_server"
                resource_name = safe_name(f"real_server_{import_id}")

        elif is_group_path(block.path):
            m = re.fullmatch(r"/c/slb/group\s+(\S+)", block.path)
            if m:
                import_id = m.group(1)
                resource_type = "alteon_server_group"
                resource_name = safe_name(f"server_group_{import_id}")

        elif is_virt_path(block.path):
            m = re.fullmatch(r"/c/slb/virt\s+(\S+)", block.path)
            parsed = parse_commands(block.commands)
            # Nur importieren, wenn auch eine Native-Resource erzeugt wird.
            if m and one_value(parsed, "vip"):
                import_id = m.group(1)
                resource_type = "alteon_virtual_server"
                resource_name = safe_name(f"virtual_server_{import_id}")

        if resource_type and resource_name and import_id:
            key = (resource_type, resource_name)
            if key not in seen:
                imports.append({
                    "resource": f"{resource_type}.{resource_name}",
                    "id": import_id,
                })
                seen.add(key)

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
    parser = argparse.ArgumentParser(
        description="Konvertiert Alteon-SLB-Konfigurationsdump in Terraform."
    )

    print(
        f"Alteon Configuration Converter "
        f"v{__version__} "
        f"(c) 2026 Michael Schwenke"
    )

    parser.add_argument("input", type=Path, help="Alteon-Konfigurationsdump")
    parser.add_argument("-o", "--output", type=Path, default=Path("main.tf"), help="Zieldatei, Default: main.tf")
    parser.add_argument("-i", "--import-file", help="Generate Terraform import blocks")
    parser.add_argument(
        "--cli-only",
        action="store_true",
        help="Auch Real/Virt/Service als alteon_cli_command ausgeben statt Native-Resources.",
    )
    args = parser.parse_args()

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
        or is_cli_supported_path(b.path)
    ]

    print("alteon_to_terraform_native_v3_3")
    print(f"OK: {len(relevant)} relevante Alteon-Blöcke nach {args.output} geschrieben.")
    if args.import_file:
        print(f"OK: {len(generated_imports)} Import-Blöcke nach {args.import_file} geschrieben.")
    print("Modus:", "Native Resources" if not args.cli_only else "CLI only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())