
import json
import re
import shutil
import subprocess

# Only these predefined commands can be executed.
ALLOWED_TOOLS = {
    "get_cpu_info": ["lscpu"],
    "get_block_devices": [
        "lsblk", "-J", "-o",
        "NAME,SIZE,TYPE,MOUNTPOINT,MODEL,ROTA,TRAN"
    ],
    "get_memory_summary": ["free", "-b"],
    "get_gpu_info": ["lspci"],
    "get_dmi_memory": ["dmidecode", "-t", "memory"],
}


def discover_tools():
    """Register only tools whose Linux utilities are installed."""
    available = {}
    for name, command in ALLOWED_TOOLS.items():
        if shutil.which(command[0]):
            available[name] = command
    return available


def parse_tool_output(tool_name, output):
    if tool_name == "get_block_devices":
        return json.loads(output)

    if tool_name == "get_cpu_info":
        data = {}
        for line in output.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        return data

    if tool_name == "get_memory_summary":
        for line in output.splitlines():
            if line.startswith("Mem:"):
                values = line.split()
                return {
                    "total_bytes": int(values[1]),
                    "used_bytes": int(values[2]),
                    "free_bytes": int(values[3]),
                    "available_bytes": int(values[6]),
                }
        return {"status": "Memory data unavailable"}

    if tool_name == "get_gpu_info":
        devices = [
            line.strip() for line in output.splitlines()
            if line.strip()
        ]
        return {"devices": devices}

    
    if tool_name == "get_dmi_memory":
        maximum = re.search(r"Maximum Capacity:\s*(.+)", output)
        devices = re.findall(r"Size:\s*(.+)", output)

        installed = [
            item.strip()
            for item in devices
            if "No Module Installed" not in item
        ]

        # WSL or restricted systems may expose no DMI data.
        if not maximum and not devices:
            return {
                "status": "data_unavailable",
                "maximum_capacity": None,
                "total_slots": None,
                "used_slots": None,
                "free_slots": None,
                "installed_modules": None,
                "message": "Physical RAM slot information is unavailable."
            }

        return {
            "status": "available",
            "maximum_capacity": maximum.group(1) if maximum else None,
            "total_slots": len(devices),
            "used_slots": len(installed),
            "free_slots": len(devices) - len(installed),
            "installed_modules": installed
        }


    return {"raw_output": output}


def execute_system_tool(tool_name, arguments=None):
    available = discover_tools()

    if tool_name not in ALLOWED_TOOLS:
        return {"error": "Unauthorized tool execution rejected"}

    if tool_name not in available:
        return {
            "error": f"Required utility for {tool_name} is unavailable",
            "status": "data_unavailable",
        }

    if arguments not in (None, {}):
        return {"error": "Unexpected tool arguments rejected"}

    try:
        result = subprocess.run(
            available[tool_name],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
            check=False,
        )

        if result.returncode != 0:
            return {
                "error": result.stderr.strip() or "Command failed",
                "status": "data_unavailable",
            }

        return parse_tool_output(tool_name, result.stdout)

    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 5 seconds"}

    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {"error": str(error)}
