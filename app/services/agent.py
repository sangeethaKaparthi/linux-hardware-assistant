
import json
import ollama

from app.services.executor import (
    ALLOWED_TOOLS,
    discover_tools,
    execute_system_tool,
)

MODEL = "llama3.2:3b"


SYSTEM_PROMPT = """
You are a Local Linux Hardware Q&A Assistant.

Answer questions using ONLY verified JSON returned by
the hardware inspection tools.

STRICT ACCURACY RULES:

1. Never invent or assume hardware specifications.
2. CPU:
   - CPU(s) means logical CPUs/threads.
   - Core(s) per socket means physical cores per socket.
   - Never report logical CPUs as physical cores.
3. RAM:
   - total_bytes means total memory reported by the system.
   - available_bytes means memory currently available.
   - used_bytes means memory currently used.
   - Never confuse total RAM with available RAM.
4. GPU:
   - Report only devices identified by system data.
   - Do not assume that a virtual graphics device means
     there is no physical GPU.
5. Storage:
   - Use the exact device names, sizes and types returned
     by the storage tool.
   - Do not invent device purposes or capacities.
6. RAM upgrades:
   - Only report slots and maximum capacity if verified
     by dmidecode or another reliable hardware source.
   - Missing slot information does NOT mean RAM is soldered.
   - Never claim upgradeability without sufficient evidence.
7. If information is missing, explicitly say:
   "I cannot determine this hardware detail from system data."
8. Explain when WSL or virtualization limits hardware visibility.
9. Never execute arbitrary shell commands.
10. Keep answers clear and concise.
"""


TOOL_DESCRIPTIONS = {
    "get_cpu_info": "Get CPU model, cores, threads and architecture.",
    "get_block_devices": "Get storage device information.",
    "get_memory_summary": "Get installed system memory and usage.",
    "get_gpu_info": "Get detected graphics and PCI devices.",
    "get_dmi_memory": "Get physical RAM slots and maximum capacity."
}


class HardwareAgent:

    def __init__(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.available_tools = discover_tools()

    def get_tool_definitions(self):
        tools = []

        for name in self.available_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": TOOL_DESCRIPTIONS[name],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            })

        return tools

    def ask(self, question):
        self.messages.append({
            "role": "user",
            "content": question
        })

        try:
            for _ in range(5):
                response = ollama.chat(
                    model=MODEL,
                    messages=self.messages,
                    tools=self.get_tool_definitions()
                )

                message = response.message
                self.messages.append(message)

                if not message.tool_calls:
                    return message.content

                for call in message.tool_calls:
                    name = call.function.name
                    arguments = call.function.arguments or {}

                    result = execute_system_tool(name, arguments)

                    self.messages.append({
                        "role": "tool",
                        "tool_name": name,
                        "content": json.dumps(result)
                    })

            return "Unable to complete the request within the tool-call limit."

        except Exception as error:
            return f"Assistant error: {error}"
