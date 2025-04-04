
from __future__ import annotations

from datetime import datetime, date

import enum

from sqlalchemy import String, Text, ForeignKey, Date, DateTime, Enum

from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

from db_config.storage_config import Base, intpk, chapter, affair, pictures, points, user_fk


class Item(Base):
    __tablename__ = "item_tm"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    categories: Mapped[str] = mapped_column(
        MutableList.as_mutable(ARRAY(String(30))), nullable=True
    )
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    item_user: Mapped[list["User"]] = relationship(
        back_populates="user_item",
    )
    item_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_item", cascade="all, delete-orphan"
    )
    item_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_item", cascade="all, delete-orphan"
    )
    item_service: Mapped[list["Service"]] = relationship(
        back_populates="service_item", cascade="all, delete-orphan"
    )
    # ..
    item_sch_r: Mapped[list["ScheduleRent"]] = relationship(
        back_populates="sch_r_item", cascade="all, delete-orphan"
    )
    item_sch_s: Mapped[list["ScheduleService"]] = relationship(
        back_populates="sch_s_item", cascade="all, delete-orphan"
    )
    # ..
    item_rrf: Mapped[list["ReserveRentFor"]] = relationship(
        back_populates="rrf_item", cascade="all, delete-orphan"
    )

    def __str__(self):
        return str(self.id)


class Rent(Base):
    __tablename__ = "rent_tm"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    rent_belongs: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    rent_user: Mapped[list["User"]] = relationship(
        back_populates="user_rent",
    )
    rent_item: Mapped[list["Item"]] = relationship(
        back_populates="item_rent",
    )
    rent_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_rent", cascade="all, delete-orphan"
    )
    rent_sch_r: Mapped[list["ScheduleRent"]] = relationship(
        back_populates="sch_r_rent", cascade="all, delete-orphan"
    )
    rent_rrf: Mapped[list["ReserveRentFor"]] = relationship(
        back_populates="rrf_rent",
    )

    def __str__(self):
        return str(self.id)


class Service(Base):
    __tablename__ = "service_tm"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    file: Mapped[pictures]
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    service_belongs: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    service_user: Mapped[list["User"]] = relationship(
        back_populates="user_service",
    )
    service_item: Mapped[list["Item"]] = relationship(
        back_populates="item_service",
    )
    service_cmt: Mapped[list["Comment"]] = relationship(
        back_populates="cmt_service", cascade="all, delete-orphan"
    )
    service_sch_s: Mapped[list["ScheduleService"]] = relationship(
        back_populates="sch_s_service", cascade="all, delete-orphan"
    )
    service_rsf: Mapped[list["ReserveServicerFor"]] = relationship(
        back_populates="rsf_service", cascade="all, delete-orphan"
    )
    service_dump_s: Mapped[list["DumpService"]] = relationship(
        back_populates="dump_s_service", cascade="all, delete-orphan"
    )

    def __str__(self):
        return str(self.id)


class ScheduleRent(Base):
    __tablename__ = "sch_r"

    id: Mapped[intpk]
    title: Mapped[chapter]
    description: Mapped[affair]
    # ...
    start: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    start_end: Mapped[datetime] = mapped_column(
        MutableList.as_mutable(ARRAY(DateTime)), nullable=True
    )
    # ...
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    sch_r_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    sch_r_rent_id: Mapped[int] = mapped_column(
        ForeignKey("rent_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    sch_r_user: Mapped[list["User"]] = relationship(
        back_populates="user_sch_r",
    )
    sch_r_item: Mapped[list["Item"]] = relationship(
        back_populates="item_sch_r",
    )
    sch_r_rent: Mapped[list["Rent"]] = relationship(
        back_populates="rent_sch_r",
    )

    def __str__(self):
        return str(self.id)


class MyEnum(enum.Enum):
    event = 1
    holiday = 2
    birthday = 3


class ScheduleService(Base):
    __tablename__ = "sch_s"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), nullable=True)
    title: Mapped[chapter]
    description: Mapped[affair]
    # ...
    type_on: Mapped[str] = mapped_column(Enum(MyEnum), nullable=True)
    number_on: Mapped[date] = mapped_column(Date, nullable=True)
    there_is: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    free: Mapped[datetime] = mapped_column(
        MutableList.as_mutable(ARRAY(DateTime)), nullable=True
    )
    # ...
    created_at: Mapped[points]
    modified_at: Mapped[points]
    # ...
    owner: Mapped[user_fk]
    # ...
    sch_s_item_id: Mapped[int] = mapped_column(
        ForeignKey("item_tm.id", ondelete="CASCADE"), nullable=False
    )
    sch_s_service_id: Mapped[int] = mapped_column(
        ForeignKey("service_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    sch_s_user: Mapped[list["User"]] = relationship(
        back_populates="user_sch_s",
    )
    sch_s_service: Mapped[list["Service"]] = relationship(
        back_populates="service_sch_s",
    )
    sch_s_item: Mapped[list["Item"]] = relationship(
        back_populates="item_sch_s",
    )
    sch_s_rsf: Mapped[list["ReserveServicerFor"]] = relationship(
        back_populates="rsf_sch_s",
    )

    def __str__(self):
        return str(self.id)


class DumpService(Base):
    __tablename__ = "dump_s"

    id: Mapped[intpk]
    title: Mapped[datetime] = mapped_column(DateTime, unique=True, index=True)
    # ...
    owner: Mapped[user_fk]
    dump_s_service_id: Mapped[int] = mapped_column(
        ForeignKey("service_tm.id", ondelete="CASCADE"), nullable=False
    )
    # ...
    dump_s_user: Mapped[list["User"]] = relationship(
        back_populates="user_dump_s",
    )
    dump_s_service: Mapped[list["Service"]] = relationship(
        back_populates="service_dump_s",
    )

    def __str__(self):
        return str(self.id)


class Slider(Base):
    __tablename__ = "slider"
    id: Mapped[intpk]
    title: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    # ...
    id_sl: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    file: Mapped[pictures]
    # ...
    created_at: Mapped[points]
    modified_at: Mapped[points]
