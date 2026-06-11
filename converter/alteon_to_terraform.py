#!/usr/bin/env python3
'''
alteon_to_terraform_native_v2.py
Version: native-v2

Konvertiert ausgewählte Alteon-CLI-Dump-Blöcke in Terraform
für den Radware/alteon Provider.

Aktuell:
  - /c/slb/real <id>                 -> alteon_real_server
  - /c/slb/virt <id>                 -> alteon_virtual_server, alle IDs
  - /c/slb/virt <id>/service ...     -> alteon_virtual_service, alle IDs
  - /c/slb/group <id>                -> alteon_cli_command
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
        re.fullmatch(r"/c/slb/group\s+\S+", path)
        or re.fullmatch(r"/c/slb/ssl/certs/group\s+\S+", path)
    )


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

    ipaddr = one_value(parsed, "rip")
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

    name = f"real_server_{index}"
    lines = [
        f'resource "alteon_real_server" "{safe_name(name)}" {{',
        f'  index = {hcl_value(index)}',
        *hcl_block("elements", attrs, indent=2),
        "}",
    ]
    return name, lines


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
        elif native and is_virt_path(block.path):
            rendered = block_to_virtual_server(block)

        if rendered:
            name, lines = rendered
            # Absicherung gegen doppelte Namen, falls IDs Sonderzeichen enthalten.
            unique_name(name, native_resource_names)
            out.extend(lines)
            out.append("")
        elif is_cli_supported_path(block.path):
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
            if is_real_path(block.path) or is_virt_path(block.path) or is_virt_service_path(block.path):
                out.extend(cli_command_to_hcl(block, used_cli_names))
                out.append("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Konvertiert Alteon-SLB-Konfigurationsdump in Terraform."
    )
    parser.add_argument("input", type=Path, help="Alteon-Konfigurationsdump")
    parser.add_argument("-o", "--output", type=Path, default=Path("main.tf"), help="Zieldatei, Default: main.tf")
    parser.add_argument(
        "--cli-only",
        action="store_true",
        help="Auch Real/Virt/Service als alteon_cli_command ausgeben statt Native-Resources.",
    )
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8", errors="replace")
    blocks = parse_alteon_config(text)
    hcl = blocks_to_terraform(blocks, native=not args.cli_only)
    args.output.write_text(hcl, encoding="utf-8")

    relevant = [
        b for b in blocks
        if is_real_path(b.path)
        or is_virt_path(b.path)
        or is_virt_service_path(b.path)
        or is_cli_supported_path(b.path)
    ]

    print("alteon_to_terraform_native_v2")
    print(f"OK: {len(relevant)} relevante Alteon-Blöcke nach {args.output} geschrieben.")
    print("Modus:", "Native Resources" if not args.cli_only else "CLI only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())