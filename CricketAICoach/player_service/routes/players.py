from fastapi import APIRouter, HTTPException
from schemas.player import PlayerCreate, PlayerResponse
from services.player_service import create_player, get_player

router = APIRouter(prefix="/players", tags=["Players"])


@router.post("/", response_model=PlayerResponse)
def create(player: PlayerCreate):
    player_id = create_player(player)
    return {
        "id": player_id,
        "name": player.name,
        "batting_hand": player.batting_hand,
        "level": player.level
    }


@router.get("/{player_id}", response_model=PlayerResponse)
def fetch(player_id: int):
    row = get_player(player_id)

    if not row:
        raise HTTPException(status_code=404, detail="Player not found")

    return dict(row)