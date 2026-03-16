#!/usr/bin/env python3
"""
Spotify OAuth 인증 스크립트

MCP 서버 사용 전에 한 번만 실행하여 Spotify 계정을 연결합니다.
브라우저가 열리면 Spotify 로그인 후 권한을 허용해주세요.
"""

import os
from pathlib import Path

# .env 파일 로드 (프로젝트 루트 기준)
load_dotenv = None
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass

# 환경 변수 확인
required_vars = ["SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET"]
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    print("오류: 다음 환경 변수를 설정해주세요:")
    for v in missing:
        print(f"  - {v}")
    print("\n1. .env.example을 복사하여 .env 파일을 만들고,")
    print("2. Spotify Developer Dashboard에서 발급받은 Client ID/Secret을 입력하세요:")
    print("   https://developer.spotify.com/dashboard")
    exit(1)

# 기본 리다이렉트 URI 설정 (없으면)
if not os.environ.get("SPOTIPY_REDIRECT_URI"):
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:7777/callback"

from spotipy.oauth2 import SpotifyOAuth

# 한 번에 모든 권한 요청 (나중에 재인증 방지)
SCOPE = (
    "user-read-email user-read-private "
    "user-read-playback-state user-read-currently-playing user-modify-playback-state "
    "user-read-recently-played user-top-read user-read-playback-position "
    "user-library-read user-library-modify "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-follow-read user-follow-modify"
)
CACHE_PATH = os.path.join(os.path.dirname(__file__), ".spotify_cache")

print("Spotify 연결 중...")
print("브라우저가 열리면 로그인 후 권한을 허용해주세요.\n")

auth = SpotifyOAuth(
    scope=SCOPE,
    cache_path=CACHE_PATH,
    open_browser=True,
)

# 토큰 획득 (브라우저 열림 또는 캐시 사용)
token = auth.get_access_token(as_dict=False)

if token:
    # 사용자 정보 확인
    import spotipy
    sp = spotipy.Spotify(auth=token)
    user = sp.current_user()
    print(f"\n✅ Spotify 연결 완료! ({user['display_name']})")
    print(f"토큰이 {CACHE_PATH} 에 저장되었습니다.")
else:
    print("\n❌ 인증에 실패했습니다. 다시 시도해주세요.")
