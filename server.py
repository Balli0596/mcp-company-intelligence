from mcp.server.fastmcp import FastMCP
import requests

# --- TOON Utility Class ---
class ToonSerializer:

    @staticmethod
    def serialize(table_name, data):
        if not data:
            return f"{table_name}[0]{{}}:"

        # Extract columns
        columns = list(data[0].keys())

        # Header
        header = f"{table_name}[{len(data)}]{{{','.join(columns)}}}:"

        # Rows
        rows = []
        for item in data:
            row = ",".join(str(item[col]) for col in columns)
            rows.append(row)

        return header + "\n" + "\n".join(rows)

# --- Initialize MCP Server ---
mcp = FastMCP("AI Company MCP")

@mcp.tool()
def get_director(din: int):
    """Fetch director details via DIN in TOON format."""
    url = f"http://localhost:8000/director/{din}"
    response = requests.get(url)
    # Returns: name:John|din:12345|status:active
    return ToonSerializer.serialize(response.json())

@mcp.tool()
def get_company(company_name: str, professionalid: int = 3):
    """Fetch company details in compact TOON format."""
    url = f"http://localhost:8000/company/{company_name}?professionalid={professionalid}"
    response = requests.get(url)
    data = response.json()
    
    companies = data.get("company", [])
    if not companies:
        return "err:no_company_found"

    # We return a header and the serialized list
    result = f"prof_id:{professionalid}\n"
    result += ToonSerializer.serialize(companies)
    return result

@mcp.tool()
def get_party_details(cin: str):
    """Fetch related party details in TOON format."""
    url = f"http://localhost:8000/related-details/{cin}"
    response = requests.get(url)
    return ToonSerializer.serialize(response.json())

@mcp.tool()
def get_client(cid: int):
    """Fetch full client profile in TOON format."""
    url = f"http://localhost:8000/client/{cid}"
    response = requests.get(url)
    return ToonSerializer.serialize(response.json())

# --- Run MCP Server ---
if __name__ == "__main__":
    mcp.run()