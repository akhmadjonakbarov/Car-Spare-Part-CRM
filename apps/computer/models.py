from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from apps.base.models import Base


class Ram(Base):
    __tablename__ = 'rams'
    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer, index=True)
    computers = relationship(
        "Computer", secondary="rams_computers", back_populates="rams")


class Rom(Base):
    __tablename__ = 'roms'
    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer)
    disk = Column(String(length=25))
    computers = relationship(
        "Computer", secondary="roms_computers", back_populates="roms")


class Computer(Base):
    __tablename__ = 'computers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))

    category = relationship("Category", back_populates="computers")
    company = relationship("Company", back_populates="computers")
    rams = relationship("Ram", secondary="rams_computers",
                        back_populates="computers")
    roms = relationship(
        "Rom", secondary="roms_computers", back_populates="computers")
    processors = relationship(
        "Processor", secondary="processors_computers", back_populates="computers")
    displays = relationship(
        "Display", secondary="computer_display", back_populates="computers")


class RamComputer(Base):
    __tablename__ = 'rams_computers'
    ram_id = Column(Integer, ForeignKey('rams.id'))
    computer_id = Column(Integer, ForeignKey('computers.id'))


class RomComputer(Base):
    __tablename__ = 'roms_computers'
    rom_id = Column(Integer, ForeignKey('roms.id'))
    computer_id = Column(Integer, ForeignKey('computers.id'))


class Processor(Base):
    __tablename__ = 'processors'
    name = Column(String, index=True)
    gens = relationship('Gen', back_populates='processor')
    computers = relationship(
        "Computer", secondary="processors_computers", back_populates="processors")


class Gen(Base):
    __tablename__ = 'gens'
    name = Column(String, index=True)
    processor_id = Column(Integer, ForeignKey('processors.id'))
    processor = relationship("Processor", back_populates="gens")


class ProcessorComputer(Base):
    __tablename__ = 'processors_computers'
    computer_id = Column(Integer, ForeignKey('computers.id'))
    processor_id = Column(Integer, ForeignKey('processors.id'))


# Display Model
class Display(Base):
    __tablename__ = 'displays'
    name = Column(String, nullable=False)

    # Many-to-many relationships
    display_sizes = relationship(
        'DSize', secondary='display_dsize', back_populates='displays')
    resolutions = relationship(
        'Resolution', secondary='display_resolution', back_populates='displays')
    refresh_rates = relationship(
        'RefreshRate', secondary='display_refresh_rate', back_populates='displays')
    computers = relationship(
        'Computer', secondary='computer_display', back_populates='displays')


# DSize Model
class DSize(Base):
    __tablename__ = 'dsize'
    value = Column(Float)
    displays = relationship(
        'Display', secondary='display_dsize', back_populates='display_sizes')


# DisplayDSize Association Table
class DisplayDSize(Base):
    __tablename__ = 'display_dsize'
    display_id = Column(Integer, ForeignKey('displays.id'))
    dsize_id = Column(Integer, ForeignKey('dsize.id'))


# Resolution Model
class Resolution(Base):
    __tablename__ = 'resolutions'
    value = Column(String)
    displays = relationship(
        'Display', secondary='display_resolution', back_populates='resolutions')


# DisplayResolution Association Table
class DisplayResolution(Base):
    __tablename__ = 'display_resolution'
    display_id = Column(Integer, ForeignKey('displays.id'))
    resolution_id = Column(Integer, ForeignKey('resolutions.id'))


# RefreshRate Model
class RefreshRate(Base):
    __tablename__ = 'refresh_rates'
    value = Column(Integer)
    displays = relationship(
        'Display', secondary='display_refresh_rate', back_populates='refresh_rates')


# DisplayRefreshRate Association Table
class DisplayRefreshRate(Base):
    __tablename__ = 'display_refresh_rate'
    display_id = Column(Integer, ForeignKey('displays.id'))
    refresh_rate_id = Column(Integer, ForeignKey('refresh_rates.id'))


class ComputerDisplay(Base):
    __tablename__ = 'computer_display'
    id = Column(Integer, primary_key=True, index=True)
    display_id = Column(Integer, ForeignKey('displays.id'))
    computer_id = Column(Integer, ForeignKey('computers.id'))
