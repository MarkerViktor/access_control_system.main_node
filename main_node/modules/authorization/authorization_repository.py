from typing import Optional
from datetime import datetime

from main_node.utils import Repository
from .authorization_entities import AdminToken, RoomLoginToken, RoomTempToken


class AuthorizationRepository(Repository):
    async def create_room_temp_token(self, room_id: int, valid_before: datetime) -> RoomTempToken:
        query = 'insert into "RoomTempToken" ("room_id", "valid_before") values ($1, $2) returning *'
        record = await self._conn.fetchrow(query, room_id, valid_before)
        return RoomTempToken.parse_obj(record)

    async def delete_room_temp_token(self, room_id: int) -> None:
        query = 'delete from "RoomTempToken" where "room_id" = $1'
        await self._conn.execute(query, room_id)

    async def get_room_temp_token(self, token: str) -> Optional[RoomTempToken]:
        query = 'select * from "RoomTempToken" where "token" = $1'
        if record := await self._conn.fetchrow(query, token):
            return RoomTempToken.parse_obj(record)
        else:
            return None

    async def get_room_login_token(self, token: str) -> Optional[RoomLoginToken]:
        query = 'select * from "RoomLoginToken" where "token" = $1'
        if record := await self._conn.fetchrow(query, token):
            return RoomLoginToken.parse_obj(record)
        else:
            return None

    async def get_admin_token(self, token: str) -> Optional[AdminToken]:
        query = 'select * from "AdminToken" where "token" = $1'
        if record := await self._conn.fetchrow(query, token):
            return AdminToken.parse_obj(record)
        else:
            return None
