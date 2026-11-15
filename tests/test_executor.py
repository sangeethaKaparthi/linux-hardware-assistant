
from unittest.mock import patch

from app.services.executor import (
    execute_system_tool,
    parse_tool_output,
)


def test_unauthorized_command_is_rejected():
    result = execute_system_tool("delete_files")
    assert "error" in result
    assert "Unauthorized" in result["error"]


def test_cpu_output_is_parsed():
    output = """
Architecture: x86_64
CPU(s): 8
Model name: Intel Core i5
"""
    result = parse_tool_output("get_cpu_info", output)

    assert result["Architecture"] == "x86_64"
    assert result["CPU(s)"] == "8"


def test_memory_output_is_parsed():
    output = "Mem: 8000000000 2000000000 1000000000 0 5000000000 5500000000"
    result = parse_tool_output("get_memory_summary", output)

    assert result["total_bytes"] == 8000000000
    assert result["available_bytes"] == 5500000000


def test_block_devices_json_is_parsed():
    result = parse_tool_output(
        "get_block_devices",
        '{"blockdevices": []}'
    )
    assert result["blockdevices"] == []


def test_dmi_memory_is_parsed():
    output = """
Maximum Capacity: 64 GB
Size: 16 GB
Size: No Module Installed
"""
    result = parse_tool_output("get_dmi_memory", output)

    assert result["total_slots"] == 2
    assert result["used_slots"] == 1
    assert result["free_slots"] == 1


def test_shell_injection_tool_name_is_rejected():
    result = execute_system_tool("get_cpu_info; rm -rf /")
    assert "error" in result


def test_missing_dmi_information_is_reported_as_unavailable():
    from app.services.executor import parse_tool_output

    result = parse_tool_output("get_dmi_memory", "")

    assert result["status"] == "data_unavailable"
    assert result["total_slots"] is None
    assert result["maximum_capacity"] is None