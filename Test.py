import os

from coreaiauth import AuthConfig, AuthnClient, Environment, AuthType

METADATA_ASSET_ID = "6488578756455985859"
METADATA_EXPERIENCE_ID = "5417bd43-1e9b-44e0-9a2f-31cbd351434a"
METADATA_HEADERS = "headers"
METADATA_CORP_ID = "ssahu16"
METADATA_EMAIL = "sumeet_sahu@intuit.com"
METADATA_PROJECT_ID = "8794421765669716971"
METADATA_ORIGINATING_ASSET_ALIAS = "Intuit.platformexps.tools.codiumaicodiumate"
ENV_VAR_APP_ID = "6488578756455985859"

context = {
    # Populate this with experience ID for your usecase
    METADATA_EXPERIENCE_ID: "5417bd43-1e9b-44e0-9a2f-31cbd351434a",

    # Populate this with your client asset alias linked to above experience ID which you will be using to make LLM call
    METADATA_ORIGINATING_ASSET_ALIAS: "Intuit.platformexps.tools.codiumaicodiumate"
}


def update_credentials(context):
    os.environ[ENV_VAR_APP_ID] = context[METADATA_ORIGINATING_ASSET_ALIAS]

    client = AuthnClient(
        AuthConfig(
            env=Environment.E2E,
            authType=AuthType.USER,
            appId=context[METADATA_ORIGINATING_ASSET_ALIAS]
        )
    )
    # Copy getAccessToken verification URL in the browser to initiate SSO authentication
    token_details = client.generate_header()
    context.update(
        {
            METADATA_HEADERS: token_details.headers,
            METADATA_CORP_ID: token_details.corpId,
            METADATA_EMAIL: token_details.email
        }
    )


update_credentials(context)

INTUIT_GENOS_HEADER = {
    "intuit_experience_id": context[METADATA_EXPERIENCE_ID],
    "intuit_originating_assetalias": context[METADATA_ORIGINATING_ASSET_ALIAS],
}

INTUIT_AUTHN_HEADERS = INTUIT_GENOS_HEADER | context[METADATA_HEADERS]

print(INTUIT_AUTHN_HEADERS)

BASE_URL = "https://llmexecution-e2e.api.intuit.com/v3/{intuit_genos_model_id}"

from openai import OpenAI
from IPython.display import JSON  # For pretty printing

# For using non-OpenAI model
BASE_URL_WITH_INTUIT_GENOS_MODEL_ID = BASE_URL.format(intuit_genos_model_id="anthropic.claude-3-haiku-20240307-v1-0")

client = OpenAI(
    api_key="xxx",  # No OP as we will use INTUIT_AUTHN_HEADERS
    base_url=BASE_URL_WITH_INTUIT_GENOS_MODEL_ID
)

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

print(response.choices[0].message.content)