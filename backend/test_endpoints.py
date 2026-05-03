import requests

KEY  = "7ea5b0e395msh5688a5c3c54ddfep17130fjsn23fdd59f6952"
HOST = "instagram-api-fast-reliable-data-scraper.p.rapidapi.com"

headers = {
    "x-rapidapi-key" : KEY,
    "x-rapidapi-host": HOST,
    "Content-Type"   : "application/json"
}

# We know this works:
# GET /user_id_by_username?username=X → {'UserID': 43952911107, 'UserName': 'affordablemobiles.co.uk'}

user_id  = 43952911107
username = "affordablemobiles.co.uk"

# Try all possible profile endpoint paths
profile_endpoints = [
    f"/user_profile_data?user_id={user_id}",
    f"/get_user_profile?user_id={user_id}",
    f"/user_info?user_id={user_id}",
    f"/profile?user_id={user_id}",
    f"/get_profile?user_id={user_id}",
    f"/user_data?user_id={user_id}",
    f"/user?user_id={user_id}",
    f"/profile_data?user_id={user_id}",
    f"/user_profile?user_id={user_id}",
    f"/get_user?user_id={user_id}",
    f"/user_details?user_id={user_id}",
    f"/account?user_id={user_id}",
    f"/user_profile_data?id={user_id}",
    f"/user_info?id={user_id}",
    f"/profile?id={user_id}",
]

print("=" * 60)
print("Testing PROFILE endpoints...")
print("=" * 60)

for endpoint in profile_endpoints:
    try:
        import http.client
        conn = http.client.HTTPSConnection(HOST)
        conn.request("GET", endpoint, headers=headers)
        res  = conn.getresponse()
        data = res.read().decode("utf-8")
        print(f"\nEndpoint: {endpoint}")
        print(f"Status: {res.status}")
        print(f"Response: {data[:200]}")
        if res.status == 200 and 'does not exist' not in data:
            print("✅ FOUND WORKING ENDPOINT!")
            break
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 60)
print("Testing POSTS/MEDIA endpoints...")
print("=" * 60)

media_endpoints = [
    f"/user_media?user_id={user_id}",
    f"/user_posts?user_id={user_id}",
    f"/get_user_media?user_id={user_id}",
    f"/user_feed?user_id={user_id}",
    f"/media?user_id={user_id}",
    f"/posts?user_id={user_id}",
    f"/user_timeline?user_id={user_id}",
    f"/get_posts?user_id={user_id}",
    f"/user_media?id={user_id}",
    f"/user_posts?id={user_id}",
    f"/feed?user_id={user_id}",
    f"/user_media_data?user_id={user_id}",
]

for endpoint in media_endpoints:
    try:
        conn = http.client.HTTPSConnection(HOST)
        conn.request("GET", endpoint, headers=headers)
        res  = conn.getresponse()
        data = res.read().decode("utf-8")
        print(f"\nEndpoint: {endpoint}")
        print(f"Status: {res.status}")
        print(f"Response: {data[:200]}")
        if res.status == 200 and 'does not exist' not in data:
            print("✅ FOUND WORKING MEDIA ENDPOINT!")
            break
    except Exception as e:
        print(f"Error: {e}")
