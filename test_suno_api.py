"""
Suno AI APIテストスクリプト
正しいエンドポイントとパラメータを確認する
"""

import requests
import json

API_KEY = "056bf3895857043c7ea5a682f5443c7f"
BASE_URL = "https://api.sunoapi.com"

# テスト1: /api/generate エンドポイント
print("=" * 60)
print("テスト1: /api/generate (POST)")
print("=" * 60)

url1 = f"{BASE_URL}/api/generate"
headers1 = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload1 = {
    "prompt": "J-Pop, Female Vocal, uplifting",
    "make_instrumental": False,
    "wait_audio": False
}

try:
    response1 = requests.post(url1, headers=headers1, json=payload1, timeout=10)
    print(f"ステータスコード: {response1.status_code}")
    print(f"レスポンスヘッダー: {dict(response1.headers)}")
    print(f"レスポンス本文: {response1.text[:500]}")
except Exception as e:
    print(f"エラー: {e}")

# テスト2: /api/custom_generate エンドポイント  
print("\n" + "=" * 60)
print("テスト2: /api/custom_generate (POST)")
print("=" * 60)

url2 = f"{BASE_URL}/api/custom_generate"
headers2 = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload2 = {
    "title": "Test Song",
    "tags": "J-Pop, Female Vocal",
    "prompt": "",
    "mv": "chirp-v4-5",
    "continue_clip_id": None,
    "continue_at": None
}

try:
    response2 = requests.post(url2, headers=headers2, json=payload2, timeout=10)
    print(f"ステータスコード: {response2.status_code}")
    print(f"レスポンスヘッダー: {dict(response2.headers)}")
    print(f"レスポンス本文: {response2.text[:500]}")
except Exception as e:
    print(f"エラー: {e}")

# テスト3: api-keyヘッダーを使用
print("\n" + "=" * 60)
print("テスト3: api-key ヘッダーで /api/generate (POST)")
print("=" * 60)

headers3 = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

try:
    response3 = requests.post(url1, headers=headers3, json=payload1, timeout=10)
    print(f"ステータスコード: {response3.status_code}")
    print(f"レスポンスヘッダー: {dict(response3.headers)}")
    print(f"レスポンス本文: {response3.text[:500]}")
except Exception as e:
    print(f"エラー: {e}")

# テスト4: GETメソッドでクレジット確認
print("\n" + "=" * 60)
print("テスト4: /api/get_limit (GET) - クレジット確認")
print("=" * 60)

url4 = f"{BASE_URL}/api/get_limit"
headers4 = {
    "Authorization": f"Bearer {API_KEY}"
}

try:
    response4 = requests.get(url4, headers=headers4, timeout=10)
    print(f"ステータスコード: {response4.status_code}")
    print(f"レスポンス: {response4.text}")
except Exception as e:
    print(f"エラー: {e}")
