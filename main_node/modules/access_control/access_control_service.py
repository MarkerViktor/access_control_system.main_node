from asyncio import to_thread
from datetime import datetime, date
from typing import Optional

import numpy as np
from pydantic import BaseModel

from face_recognition import NumpyImage, Descriptor
from face_recognition.two_step import FaceRecognizer, FaceImageNormalizer

from main_node.utils import Service, Ok, Error, Result
from .access_control_repository import AccessControlRepository
from .access_control_entities import User


class AccessControlService(Service):
    SERVICE_NAME = 'access_control'

    def __init__(self, repository: AccessControlRepository,
                 face_recognizer: FaceRecognizer,
                 face_image_normalizer: FaceImageNormalizer):
        self._repository = repository
        self._face_recognizer = face_recognizer
        self._face_image_normalizer = face_image_normalizer

    async def check_access_by_face(self, room_id: int, image: NumpyImage) -> 'Result[AccessCheck]':
        """Check user access to the room by his face."""
        if not self._face_recognizer.check_image_normalized(image):
            return Error(cause='Provided image is not normalized.')
        # Recognize face
        result = await to_thread(self._face_recognizer.recognize, image)
        if not result.is_known_face:
            return Ok(result=AccessCheck(is_known=False))
        # Get user by descriptor id
        user = await self._repository.get_user_by_descriptor_id(result.descriptor_id)
        if user is None:
            cause = f'Calculated descriptor is known, but not bound to user. (descriptor_id = {result.descriptor_id})'
            return Error(cause=cause)
        # Check user access to the room
        have_access = await self._repository.check_access_permission_exist(user.id, room_id)
        return Ok(result=AccessCheck(is_known=True, have_access=have_access, user=user))

    async def check_access_by_descriptor(self, room_id: int, descriptor: Descriptor) -> 'Result[AccessCheck]':
        """Check user access to the room by descriptor of his face."""
        if not self._face_recognizer.check_descriptor_valid(descriptor):
            return Error(cause='Provided descriptor is invalid.')
        # Get descriptor id
        result = self._face_recognizer.recognize_by_descriptor(descriptor)
        if not result.is_known_face:
            return Ok(result=AccessCheck(is_known=False))
        # Get user by descriptor id
        user = await self._repository.get_user_by_descriptor_id(result.descriptor_id)
        if user is None:
            cause = f'Provided descriptor is known, but not bound to user. (descriptor_id = {result.descriptor_id})'
            return Error(cause=cause)
        # Check user access to the room
        have_access = await self._repository.check_access_permission_exist(user.id, room_id)
        return Ok(result=AccessCheck(is_known=True, have_access=have_access, user=user))

    async def record_visit(self, room_id: int, user_id: int, datetime_: datetime) -> 'Result[VisitRecording]':
        """Record information about room visiting if access permission exist."""
        # Check permission to the room exist
        if not await self._repository.check_access_permission_exist(user_id, room_id):
            return Ok(result=VisitRecording(allowed=False))
        # Write no visit to database
        visit = await self._repository.create_visit_report(room_id, user_id, datetime_)
        return Ok(result=VisitRecording(allowed=True, visit_id=visit.id))

    async def calculate_descriptor(self, image: NumpyImage) -> 'Result[AnonymousDescriptor]':
        """Calculate face descriptor based on given image."""
        if not self._face_image_normalizer.check_image_valid(image):
            return Error(cause="Provided image is invalid.")

        # Normalize image
        normalized_image = await to_thread(self._face_image_normalizer.normalize, image)
        if normalized_image is None:
            return Error(cause="Can't normalize image. Maybe there is no face.")

        # Calculate descriptor
        descriptor = await to_thread(self._face_recognizer.calculate_descriptor, normalized_image)
        anonymous_descriptor = AnonymousDescriptor(features=list(descriptor))

        return Ok(result=anonymous_descriptor)

    async def _load_descriptors(self) -> None:
        """Load descriptors from DB to the ._face_recognizer()."""
        descriptors = await self._repository.get_all_face_descriptors()
        numpy_descriptors = ((d.id, np.array(d.features)) for d in descriptors)
        self._face_recognizer.update_descriptors(numpy_descriptors)

    async def init_service(self, _) -> None:
        await self._load_descriptors()

    async def deinit_service(self, _) -> None:
        pass


class AccessCheck(BaseModel):
    is_known: bool
    have_access: Optional[bool] = None
    user: Optional[User] = None


class VisitRecording(BaseModel):
    allowed: bool
    visit_id: Optional[int] = None


class AnonymousDescriptor(BaseModel):
    features: list[float]
