import requests

BASE_URL = "http://localhost:8000"


# 🔹 Safe request wrapper
def safe_request(url):
    try:
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return {
                "error": f"API error {response.status_code}",
                "details": response.text
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_comapny_tool(company_name: str, professionalid: int = 3):

    url = f"{BASE_URL}/company/{company_name}?professionalid={professionalid}"

    return safe_request(url)
# 🔹 Tool: Get Director
def get_director_tool(din: int):
    """
    Fetch director details using professional id
    """
    url = f"{BASE_URL}/director/{din}"
    return safe_request(url)

def get_related_entity_party(cin: str):
    url = f"{BASE_URL}/related-details/{cin}"
    return safe_request(url)
# 🔹 Tool: Get Client
def get_client_tool(cid: int):
    """
    Fetch full client profile using client id
    """
    url = f"{BASE_URL}/client/{cid}"
    return safe_request(url)