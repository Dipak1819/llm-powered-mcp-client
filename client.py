from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import asyncio
from pathlib import Path
import sys
import os
from openai import OpenAI
from dotenv import load_dotenv
import json

filepath = Path(__file__).parent/".venv"/"bin"/"python3.12"
client_path = Path(__file__).parent/"server.py"

env_path = Path(__file__).parent/".env"
load_dotenv(env_path)

OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

#creating a openai client
client = OpenAI(api_key=OPEN_AI_API_KEY)

server_parms = StdioServerParameters(
    command=sys.executable,
    args = [str(client_path)],
)

async def main():
    async with stdio_client(server_parms) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            tools_list = await session.list_tools()
            tools = tools_list.model_dump()
            tool = tools.get("tools")
            tools_and_descriptions = {

            }
            for item in tool:
                tools_and_descriptions[item.get("name")]=item.get("description")
                

            prompt = input("Client Prompt: ")


            response = client.responses.create(
            model="gpt-5-mini",
            instructions= f"You are a mcp client - the list of tools available to you are {tools_and_descriptions}. Choose what tool is appropriate for the clients task and then return a json saying which tool to use and what argument to pass",
            input = prompt
            )

            #reading the LLM response
            print("LLM Response: ",response.output_text)

            decision = json.loads(response.output_text)
            print(decision)

            tool_to_invoke = decision.get("tool")
            argument_to_pass = decision.get("argument")

            tool_response = await session.call_tool(tool_to_invoke,arguments={"city":argument_to_pass})
            final_output = {
                "prompt":prompt,
                "tool_used":tool_to_invoke,
                "answer":tool_response.model_dump()
            }
            response2 = client.responses.create(
                model = "gpt-4",
                instructions="Answer the users original question using the provided mcp tool result",
                input = json.dumps(final_output)
            )
            print(response2.output_text)


if __name__ =="__main__":
    asyncio.run(main())

