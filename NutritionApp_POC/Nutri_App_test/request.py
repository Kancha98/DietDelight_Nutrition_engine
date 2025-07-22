import requests

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI5OTk5Iiwic3ViIjoiYXBwbGljYXRpb24tdXNlci1pZC0xMjMifQ.XnI1y4tkRjdiSeHwUqdmk9em-hTPojtMzbOU30nMd_Y"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get("https://app-api.spikeapi.com/v3/users/me", headers=headers)

print(response.status_code)
print(response.json())
