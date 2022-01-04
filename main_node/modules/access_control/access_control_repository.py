from datetime import datetime
from typing import Optional

from main_node.utils import Repository

from .access_control_entities import User, UserFaceDescriptor, RoomVisitReport


class AccessControlRepository(Repository):
    async def get_user_by_descriptor_id(self, descriptor_id: int) -> Optional[User]:
        query = 'select * from "User" where "id" = ' \
                '(select "user_id" from "UserFaceDescriptor" where "id" = $1)'
        if record := await self._conn.fetchrow(query, descriptor_id):
            return User.parse_obj(record)
        else:
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = 'select * from "User" where "id" = $1'
        if record := await self._conn.fetchrow(query, user_id):
            return User.parse_obj(record)
        else:
            return None

    async def check_access_permission_exist(self, user_id: int, room_id: int) -> bool:
        query = 'select from "UserRoomAccessPermission" where "room_id" = $1 and "user_id" = $2'
        return await self._conn.fetchrow(query, room_id, user_id) is not None

    async def create_visit_report(self, room_id: int, user_id: int, datetime_: datetime) -> RoomVisitReport:
        query = 'insert into "RoomVisitReport" ("room_id", "user_id", "datetime") ' \
                'values ($1, $2, $3) returning *'
        record = await self._conn.fetchrow(query, room_id, user_id, datetime_)
        return RoomVisitReport.parse_obj(record)

    async def get_all_face_descriptors(self) -> list[UserFaceDescriptor]:
        query = 'select * from "UserFaceDescriptor"'
        descriptors = []
        async with self._conn.transaction():
            async for record in self._conn.cursor(query):
                descriptors.append(UserFaceDescriptor.parse_obj(record))
        return descriptors
