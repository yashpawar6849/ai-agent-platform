"""End-to-end demo: creates a multi-tool agent and runs tasks."""
from sdk import AgentBuilder, AgentClient


def main():
    client = AgentClient("http://localhost:8000")

    agent = (
        AgentBuilder()
        .name("multi")
        .instruction("A versatile agent with many tools.")
        .tool("math_tool")
        .tool("code_tool")
        .tool("calculator_tool")
        .tool("shell_tool")
        .tool("plot_tool")
        .llm_backend("mock")
        .build()
    )

    created = client.create_agent(agent)
    print(f"Created agent: {created.name} ({created.id})")

    result = client.run_task(
        created.id, "Calculate fib(10) and verify with Python"
    )
    print(f"\nStatus: {result.status.value}")
    print(f"Result: {result.result}")
    print(f"\nEvents ({len(result.events)}):")
    for event in result.events:
        if event.type.value == "tool_call":
            print(
                f"  [Tool Call] {event.content} "
                f"-> args: {event.metadata.get('args')}"
            )
        elif event.type.value == "tool_result":
            print(f"  [Tool Result] {event.content[:60]}...")
        elif event.type.value == "final_answer":
            print(f"  [Final] {event.content}")
        else:
            print(f"  [{event.type.value}] {event.content[:50]}")

    client.close()


if __name__ == "__main__":
    main()
