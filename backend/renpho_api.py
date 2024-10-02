from vital.client import Vital
from vital.environment import VitalEnvironment
import os
import pydantic
import json
from dotenv import load_dotenv
import datetime 
load_dotenv()

# TEST BACKEND IMPLEMENTATION
from vital.client import Vital
from vital.environment import VitalEnvironment
from vital.client import Vital
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import hmac
import hashlib
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Replace with your actual secret from Vital
WEBHOOK_SECRET = "whsec_7rCYOe6720hNDKARJNiOl39r+mj/hoM6"

client = Vital(
  api_key=os.environ.get("RENPHO_API_KEY"),
  environment=VitalEnvironment.SANDBOX,
  timeout=30
)

# data = client.user.create(client_user_id="test1234")
# print(data)

#print(client.link.token(user_id="7be6df66-925c-43dc-bd94-2aade6f56396"))



# # User ID for the Renpho user
user_id = "7be6df66-925c-43dc-bd94-2aade6f56396"

# Get weight data for the last 30 days
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=30)

data = client.user.refresh(
    user_id=user_id
)

print(data)

try:
    data = client.body.get(user_id=user_id, start_date="2024-01-01")
except pydantic.ValidationError as e:
    print(e.json())

for item in data.body:
    print(item.weight)
    print(item.date)
    print("-----")