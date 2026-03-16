"""
Spotify MCP 서버

가장 많이 들은 곡, 아티스트, 최근 재생 곡 등을 조회할 수 있는 MCP 서버입니다.

사용 전에 auth_spotify.py 로 한 번 인증해야 합니다.
"""

import os

from dotenv import load_dotenv

# 스크립트 위치 기준 .env 로드 (Cursor MCP에서 cwd가 다를 수 있음)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
from mcp.server.fastmcp import FastMCP

# 기본 리다이렉트 URI
if not os.environ.get("SPOTIPY_REDIRECT_URI"):
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:7777/callback"

# auth_spotify.py와 동일한 스코프 유지
SCOPE = (
    "user-read-email user-read-private "
    "user-read-playback-state user-read-currently-playing user-modify-playback-state "
    "user-read-recently-played user-top-read user-read-playback-position "
    "user-library-read user-library-modify "
    "playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public "
    "user-follow-read user-follow-modify"
)
CACHE_PATH = os.path.join(os.path.dirname(__file__), ".spotify_cache")

mcp = FastMCP("Spotify", json_response=True)


def _get_spotify():
    """Spotify 클라이언트 반환 (인증 필요 시 에러)"""
    from spotipy.oauth2 import SpotifyOAuth
    from spotipy import Spotify

    auth = SpotifyOAuth(scope=SCOPE, cache_path=CACHE_PATH)
    token = auth.get_cached_token()
    if not token:
        return None
    return Spotify(auth_manager=auth)


@mcp.tool()
def spotify_get_top_tracks(
    time_range: str = "medium_term",
    limit: int = 20,
) -> str:
    """가장 많이 들은 곡 목록을 조회합니다.

    Args:
        time_range: 기간 (short_term=최근 4주, medium_term=최근 6개월, long_term=약 1년)
        limit: 반환할 곡 수 (1-50, 기본 20)

    Returns:
        순위, 곡명, 아티스트, 앨범 정보가 담긴 텍스트
    """
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. 먼저 auth_spotify.py를 실행하여 인증해주세요."

    try:
        results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
        lines = []
        time_names = {
            "short_term": "최근 4주",
            "medium_term": "최근 6개월",
            "long_term": "약 1년",
        }
        lines.append(f"🎵 가장 많이 들은 곡 ({time_names.get(time_range, time_range)})\n")
        for i, item in enumerate(results["items"], 1):
            track = item["track"]
            artists = ", ".join(a["name"] for a in track["artists"])
            lines.append(f"{i}. {track['name']} - {artists} ({track['album']['name']})")
        return "\n".join(lines)
    except Exception as e:
        return f"오류: {e}"


@mcp.tool()
def spotify_get_top_artists(
    time_range: str = "medium_term",
    limit: int = 20,
) -> str:
    """가장 많이 들은 아티스트 목록을 조회합니다.

    Args:
        time_range: 기간 (short_term=최근 4주, medium_term=최근 6개월, long_term=약 1년)
        limit: 반환할 아티스트 수 (1-50, 기본 20)

    Returns:
        순위, 아티스트명, 장르 정보가 담긴 텍스트
    """
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. 먼저 auth_spotify.py를 실행하여 인증해주세요."

    try:
        results = sp.current_user_top_artists(time_range=time_range, limit=limit)
        lines = []
        time_names = {
            "short_term": "최근 4주",
            "medium_term": "최근 6개월",
            "long_term": "약 1년",
        }
        lines.append(f"🎤 가장 많이 들은 아티스트 ({time_names.get(time_range, time_range)})\n")
        for i, artist in enumerate(results["items"], 1):
            genres = ", ".join(artist.get("genres", [])[:3]) or "-"
            lines.append(f"{i}. {artist['name']} (장르: {genres})")
        return "\n".join(lines)
    except Exception as e:
        return f"오류: {e}"


@mcp.tool()
def spotify_get_recently_played(limit: int = 20) -> str:
    """최근 재생한 곡 목록을 조회합니다.

    Args:
        limit: 반환할 곡 수 (1-50, 기본 20)

    Returns:
        곡명, 아티스트, 재생 시각 정보가 담긴 텍스트
    """
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. 먼저 auth_spotify.py를 실행하여 인증해주세요."

    try:
        results = sp.current_user_recently_played(limit=limit)
        lines = ["🎧 최근 재생한 곡\n"]
        for item in results.get("items", []):
            track = item["track"]
            artists = ", ".join(a["name"] for a in track["artists"])
            played_at = item.get("played_at", "")[:19].replace("T", " ")
            lines.append(f"- {track['name']} - {artists} (재생: {played_at})")
        return "\n".join(lines) if lines else "최근 재생 내역이 없습니다."
    except Exception as e:
        return f"오류: {e}"


@mcp.tool()
def spotify_get_current_user() -> str:
    """현재 연결된 Spotify 사용자 정보를 조회합니다.

    Returns:
        사용자명, 이메일, 프로필 URL 등
    """
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. 먼저 auth_spotify.py를 실행하여 인증해주세요."

    try:
        user = sp.current_user()
        lines = [
            "👤 Spotify 사용자 정보",
            f"이름: {user.get('display_name', '-')}",
            f"이메일: {user.get('email', '-')}",
            f"프로필: {user.get('external_urls', {}).get('spotify', '-')}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"오류: {e}"


@mcp.tool()
def spotify_get_now_playing() -> str:
    """지금 재생 중인 곡과 다음에 재생될 곡(큐)을 조회합니다."""
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. auth_spotify.py를 실행하여 인증해주세요."

    try:
        lines = []
        # queue() 한 번에 현재 재생 + 큐 반환
        data = sp.queue()
        if not data:
            return "재생 정보를 가져올 수 없습니다. Spotify 앱에서 재생 중인지 확인해주세요."

        current = data.get("currently_playing") if isinstance(data, dict) else None
        if current and current.get("name"):
            artists = ", ".join(a["name"] for a in current.get("artists", []))
            lines.append(f"▶ 지금 재생 중: {current['name']} - {artists}")
        else:
            lines.append("▶ 지금 재생 중: (재생 중인 곡 없음)")

        queue_list = data.get("queue", []) if isinstance(data, dict) else []
        if queue_list:
            next_track = queue_list[0]
            if next_track.get("name"):
                artists = ", ".join(a["name"] for a in next_track.get("artists", []))
                lines.append(f"⏭ 다음 곡: {next_track['name']} - {artists}")
            else:
                lines.append("⏭ 다음 곡: (큐에 없음)")
        else:
            lines.append("⏭ 다음 곡: (큐에 없음)")

        return "\n".join(lines)
    except Exception as e:
        return f"오류: {e}"


@mcp.tool()
def spotify_next_track() -> str:
    """현재 재생 중인 Spotify의 다음 곡으로 건너뜁니다.

    Spotify 앱/웹이 재생 중이어야 동작합니다.
    """
    sp = _get_spotify()
    if not sp:
        return "Spotify가 연결되지 않았습니다. auth_spotify.py를 실행하여 인증해주세요."

    try:
        sp.next_track()
        return "✅ 다음 곡으로 이동했습니다."
    except Exception as e:
        return f"오류: {e}\n재생 중인 기기가 없거나 권한이 없을 수 있습니다. rm .spotify_cache 후 auth_spotify.py를 다시 실행해보세요."


if __name__ == "__main__":
    # stdio: Cursor, Claude Desktop 등 (기본)
    # streamable-http: 원격 서버 공유 시
    mcp.run(transport="stdio")
