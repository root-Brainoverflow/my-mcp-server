# Spotify MCP 서버

Spotify에 연결하여 **가장 많이 들은 곡**, **아티스트**, **최근 재생 곡** 등을 조회할 수 있는 MCP(Model Context Protocol) 서버입니다..

## 제공 도구

| 도구 | 설명 |
|------|------|
| `spotify_get_top_tracks` | 가장 많이 들은 곡 목록 (기간/개수 조절 가능) |
| `spotify_get_top_artists` | 가장 많이 들은 아티스트 목록 |
| `spotify_get_recently_played` | 최근 재생한 곡 목록 |
| `spotify_get_current_user` | 현재 연결된 Spotify 사용자 정보 |

## 사전 요구사항

1. **Spotify 계정**
2. **Spotify Developer 앱**  
   - [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)에서 앱 생성
   - 앱 설정의 Redirect URI에 `http://localhost:8888/callback` 추가

## 설치

```bash
uv sync   # 또는 pip install -e .
```

## 설정

환경 변수 설정 (`.env` 파일 또는 터미널):

```bash
export SPOTIPY_CLIENT_ID="your-client-id"
export SPOTIPY_CLIENT_SECRET="your-client-secret"
# 선택: export SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
```

## 인증 (최초 1회)

MCP 서버 사용 전에 Spotify 계정 연결이 필요합니다:

```bash
uv run python auth_spotify.py
```

브라우저가 열리면 Spotify 로그인 후 권한을 허용해주세요. 토큰은 `.spotify_cache`에 저장됩니다.

## 실행

```bash
uv run python server.py
```

또는 MCP 클라이언트(Cursor, Claude Desktop 등)에 서버를 등록하여 사용하세요.

### Cursor 설정 예시

`.cursor/mcp.json` 또는 Cursor 설정에 추가:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/경로/my-mcp-server",
      "env": {
        "SPOTIPY_CLIENT_ID": "your-client-id",
        "SPOTIPY_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

> `cwd`에는 `server.py`와 `pyproject.toml`이 있는 프로젝트 루트 경로를 넣어주세요.

## 라이선스

MIT
