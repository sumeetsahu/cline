import os
import json
import dotenv
from coreaiauth import AuthConfig, AuthnClient, Environment, AuthType

# Load environment variables from .env file
dotenv.load_dotenv()

# Get required variables from environment
METADATA_CORP_ID = os.getenv('CORP_ID')
METADATA_EMAIL = os.getenv('EMAIL')
METADATA_EXPERIENCE_ID = os.getenv('EXPERIENCE_ID', '5417bd43-1e9b-44e0-9a2f-31cbd351434a')
METADATA_ORIGINATING_ASSET_ALIAS = os.getenv('ORIGINATING_ASSET_ALIAS', 'Intuit.platformexps.tools.codiumaicodiumate')
APP_SECRET = os.getenv('APP_SECRET')

# Validate required environment variables
if not METADATA_CORP_ID or not METADATA_EMAIL or not APP_SECRET:
    print("❌ Error: Missing required environment variables!")
    print("Please set CORP_ID, EMAIL, and APP_SECRET in your .env file.")
    print("You can copy values from .env.example and update them.")
    exit(1)

METADATA_ASSET_ID = "6488578756455985859"
METADATA_HEADERS = "headers"
METADATA_PROJECT_ID = "8794421765669716971"
ENV_VAR_APP_ID = "6488578756455985859"

context = {
    # Populate this with experience ID for your usecase
    METADATA_EXPERIENCE_ID: METADATA_EXPERIENCE_ID,

    # Populate this with your client asset alias linked to above experience ID which you will be using to make LLM call
    METADATA_ORIGINATING_ASSET_ALIAS: METADATA_ORIGINATING_ASSET_ALIAS
}

def update_credentials(context):
    os.environ[ENV_VAR_APP_ID] = context[METADATA_ORIGINATING_ASSET_ALIAS]

    print("📡 Initiating authentication process...")
    print("⚠️  You will need to copy the verification URL in your browser for SSO authentication")
    
    client = AuthnClient(
        AuthConfig(
            env=Environment.E2E,
            authType=AuthType.USER,
            appId=context[METADATA_ORIGINATING_ASSET_ALIAS]
        )
    )
    
    # Copy getAccessToken verification URL in the browser to initiate SSO authentication
    print("\n🔒 Please authenticate in the browser window that opens...\n")
    token_details = client.generate_header()
    
    context.update(
        {
            METADATA_HEADERS: token_details.headers,
            METADATA_CORP_ID: token_details.corpId,
            METADATA_EMAIL: token_details.email
        }
    )
    print("✅ Authentication completed successfully!")

# Run the authentication process
update_credentials(context)

INTUIT_GENOS_HEADER = {
    "intuit_experience_id": context[METADATA_EXPERIENCE_ID],
    "intuit_originating_assetalias": context[METADATA_ORIGINATING_ASSET_ALIAS],
}

INTUIT_AUTHN_HEADERS = INTUIT_GENOS_HEADER | context[METADATA_HEADERS]

BASE_URL = "https://llmexecution-e2e.api.intuit.com/v3/{intuit_genos_model_id}"

from openai import OpenAI

# For using non-OpenAI model
BASE_URL_WITH_INTUIT_GENOS_MODEL_ID = BASE_URL.format(intuit_genos_model_id="anthropic.claude-3-haiku-20240307-v1-0")

client = OpenAI(
    api_key="xxx",  # No OP as we will use INTUIT_AUTHN_HEADERS
    base_url=BASE_URL_WITH_INTUIT_GENOS_MODEL_ID
)

def test_auth_headers():
    try:
        print("🧪 Testing authentication headers with a sample API call...")
        # Test API call with authentication headers
        response = client.chat.completions.create(
            model="anthropic.claude-3-haiku-20240307-v1-0",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful tax assistant. Please assist me in answering my tax related queries."
                },
                {
                    "role": "user",
                    "content": "how can I make find out my marginal tax rate?"
                }
            ],
            max_tokens=500,
            temperature=0,
            extra_headers={
                **INTUIT_AUTHN_HEADERS
            }
        )
        
        # If we reach here, the API call was successful
        print("✅ Authentication successful!")
        print("\n📝 Headers used (Java compatible format):")
        # Print headers in a formatted JSON style compatible with Java
        print(json.dumps(INTUIT_AUTHN_HEADERS, indent=2))
        return True
    except Exception as e:
        print("❌ Authentication failed!")
        print(f"Error details: {str(e)}")
        return False

# Run the test
auth_successful = test_auth_headers()

# Optionally, you can process the full response only if authentication was successful
if auth_successful:
    print("\n✅ Authentication test passed. You can now use these headers for your API calls.")
    
    # Provide instructions for saving/using the headers
    print("\n💡 To use these headers in your code:")
    print("1. Copy the JSON headers above")
    print("2. Include them as part of the `Advanced: Custom Headers")
else:
    print("\n❌ Authentication test failed. Please check your credentials and try again.")
    print("You may need to:")
    print("1. Verify your CORP_ID and EMAIL in the .env file")
    print("2. Ensure you've completed the SSO flow correctly")
    print("3. Check your network connection to the Intuit API endpoints")
