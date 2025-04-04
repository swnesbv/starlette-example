from __future__ import annotations
import datetime
import sys
import os
import time
import uuid
import logging
from typing import Any
from enum import Enum
from starlette.websockets import WebSocket


class ChannelAddStatus(Enum):
    ADDED = 1
    EXIST = 2


class ChannelRemoveStatus(Enum):
    CHANNEL_REMOVED = 1
    GROUP_REMOVED = 2
    DOES_NOT_EXIST = 3


class GroupSendStatus(Enum):
    GROUP_SEND = 1
    NO_SUCH_GROUP = 2


class Channel:
    def __init__(self, websocket: WebSocket, expires: int, encoding: str) -> None:
        assert isinstance(websocket, WebSocket)
        assert isinstance(expires, int)
        assert isinstance(encoding, str) and encoding in [
            "json",
            "text",
            "bytes",
        ], "Must be in ['json', 'text', 'bytes']"
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.uuid = uuid.uuid4()
        self.created = time.time()

    async def send(self, payload: Any) -> None:
        if self.encoding == "json":
            try:
                await self.websocket.send_json(payload)
            except RuntimeError as error:
                logging.debug(error)
        elif self.encoding == "text":
            try:
                await self.websocket.send_text(payload)
            except RuntimeError as error:
                logging.debug(error)
        elif self.encoding == "bytes":
            try:
                await self.websocket.send_bytes(payload)
            except RuntimeError as error:
                logging.debug(error)
        else:
            try:
                await self.websocket.send(payload)
            except RuntimeError as error:
                logging.debug(error)
        self.created = time.time()

    async def _is_expired(self) -> None:
        return self.expires + int(self.created) < time.time()

    def __repr__(self) -> str:
        return (
            f"Channel uuid={self.uuid} expires={self.expires} encoding={self.encoding}"
        )


class ChannelBox:
    _GROUPS: dict = {}
    _GROUPS_HISTORY: dict = {}
    _HISTORY_SIZE: int = os.getenv("CHANNEL_BOX_HISTORY_SIZE", 1_048_576)

    @classmethod
    async def channel_add(cls, group_name: str, channel: Channel) -> Enum:
        if group_name not in cls._GROUPS:
            cls._GROUPS[group_name] = {}
            status = ChannelAddStatus.ADDED
        else:
            status = ChannelAddStatus.EXIST

        cls._GROUPS[group_name][channel] = 1
        return status

    @classmethod
    async def channel_remove(cls, group_name: str, channel: Channel) -> Enum:
        status = {}
        if channel in cls._GROUPS.get(group_name, {}):
            try:
                del cls._GROUPS[group_name][channel]
                status = ChannelRemoveStatus.CHANNEL_REMOVED
            except KeyError:
                status = ChannelRemoveStatus.DOES_NOT_EXIST

        if not any(cls._GROUPS.get(group_name, {})):
            try:
                del cls._GROUPS[group_name]
                status = ChannelRemoveStatus.GROUP_REMOVED
            except KeyError:
                status = ChannelRemoveStatus.DOES_NOT_EXIST

        await cls._clean_expired()
        print(" type status..!", status)
        return status

    @classmethod
    async def groups(cls) -> dict:
        return cls._GROUPS

    @classmethod
    async def groups_flush(cls) -> True:
        cls._GROUPS = {}
        return True

    @classmethod
    async def group_send(
        cls, group_name: str = "", payload: dict = {}, history: bool = False, **kwargs
    ) -> Enum:
        if history:
            cls._GROUPS_HISTORY.setdefault(group_name, [])
            cls._GROUPS_HISTORY[group_name].append(
                {
                    "payload": payload,
                    "uuid": uuid.uuid4(),
                    "datetime": datetime.datetime.now(),
                }
            )
            if sys.getsizeof(cls._GROUPS_HISTORY[group_name]) > cls._HISTORY_SIZE:
                cls._GROUPS_HISTORY[group_name] = []

        status = GroupSendStatus.NO_SUCH_GROUP
        for channel in cls._GROUPS.get(group_name, {}):
            await channel.send(payload)
            status = GroupSendStatus.GROUP_SEND

        return status

    @classmethod
    async def history(cls, group_name: str = "") -> dict:
        return (
            cls._GROUPS_HISTORY.get(group_name, {})
            if group_name
            else cls._GROUPS_HISTORY
        )

    @classmethod
    async def history_flush(cls) -> True:
        cls._GROUPS_HISTORY = {}
        return True

    @classmethod
    async def _clean_expired(cls) -> None:
        for group_name in list(cls._GROUPS):
            for channel in cls._GROUPS.get(group_name, {}):
                _is_expired = await channel._is_expired()
                if _is_expired:
                    try:
                        del cls._GROUPS[group_name][channel]
                    except KeyError:
                        logging.debug("No such channel")
            if not any(cls._GROUPS.get(group_name, {})):
                try:
                    del cls._GROUPS[group_name]
                except KeyError:
                    logging.debug("No such group")
