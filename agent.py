import requests
import json
from tools import get_director_tool, get_client_tool,get_related_entity_party,get_comapny_tool
from server import ToonSerializer
SARVAM_API_KEY = "sk_8pfijv0p_jUjmazd6vK5b4GO5MqbplZSg"

# 🔹 Sarvam endpoint (example)
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"


# 🔹 Tool execution
def execute_tool(name, args):

    if name == "get_director":
        return get_director_tool(args["din"])

    elif name == "get_client":
        return get_client_tool(args["cid"])

    elif name == "get_related_party_details":
        return get_related_entity_party(args["cin"])

    elif name == "get_company":
        return get_comapny_tool(
        args["company_name"],
        args.get("professionalid", 3)
    )

    return {"error": "Unknown tool"}

# 🔹 Send request to Sarvam

def call_sarvam(messages, tools=None):
    payload = {
        "model": "sarvam-30b",   # or latest model
        "messages": messages,
    }

    # If tool support available
    if tools:
        payload["tools"] = tools

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(SARVAM_URL, headers=headers, json=payload)
    return response.json()


# 🔹 Tool schema (LLM understanding)
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_director",
            "description": "Get director details using din",
            "parameters": {
                "type": "object",
                "properties": {
                    "din": {"type": "integer"}
                },
                "required": ["din"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_client",
            "description": "Get client details using client id",
            "parameters": {
                "type": "object",
                "properties": {
                    "cid": {"type": "integer"}
                },
                "required": ["cid"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "get_company",
        "description": "Get company details using company name",
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string"
                },
                "professionalid": {
                    "type": "integer",
                    "default": 3
                }
            },
            "required": ["company_name"]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "get_related_party_details",
            "description": "Get clients related party entity details using cin",
            "parameters": {
                "type": "object",
                "properties": {
                    "cin": {"type": "string"}
                },
                "required": ["cin"]
            }
        }
    }

]
def extract_content(response):

    # Case 1: dict response
    if isinstance(response, dict):
        return response["choices"][0]["message"]["content"]

    # Case 2: object response
    elif hasattr(response, "choices"):
        return response.choices[0].message.content

    else:
        return "Error: Unknown response format"
# 🔹 Main agent
def run_agent(user_query):
    print(f"\n🧠 User: {user_query}")

    # Step 1: Ask LLM
    response = call_sarvam(
    messages=[{"role": "user", "content": user_query}],
    tools=tools_schema
)

    
    message=response["choices"][0]["message"]
    # =========================
    # 🔥 TOOL CALL HANDLING
    # =========================
    if "tool_calls" in message:

        tool_call = message["tool_calls"][0]

        tool_name = tool_call["function"]["name"]

        args = json.loads(tool_call["function"]["arguments"])

        tool_call_id = tool_call["id"]

        tool_result = execute_tool(tool_name, args)

        final_response = call_sarvam(
            messages=[
                {"role": "user", "content": user_query},

                {
                    "role": "assistant",
                    "tool_calls": message["tool_calls"]
                },

                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_result)
                },

                {
                    "role": "system",
                    "content": """
    Convert the tool result into clean natural language.

    Rules:
    - if it has professionalid then mention it do not neglect that information
    - Show all information
    - Use readable sentence format
    - Do not return raw JSON
    - Make answer structured and beautiful
    """
                }
            ],

            tools=tools_schema
        )

        return final_response["choices"][0]["message"]["content"]

    # =========================
    # 🔹 NORMAL RESPONSE
    # =========================
    return message.get("content", "No response")
# 🔹 CLI
if __name__ == "__main__":
    while True:
        q = input("\nEnter query: ")
        ans = run_agent(q)
        print("\n🤖 Answer:\n", ans)
# esponse.choices[0].message.content