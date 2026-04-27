from pydantic import BaseModel, Field
from typing import Optional, List


# Base schema for RAM (common fields for create and update)
class RamScheme(BaseModel):
    size: int = Field(..., gt=0, description="Size of the RAM in GB, must be greater than 0")

    class Config:
        from_attributes = True


# Schema for adding a new RAM
class RamAddScheme(RamScheme):
    pass


# Schema for updating an existing RAM
class RamUpdateScheme(RamScheme):
    pass


class StorageScheme(BaseModel):
    size: int = Field(..., gt=100, description="Size of the storage")
    disk: str = Field(..., description="Disk of type (ssd or hdd)")

    class Config:
        from_attributes = True


class StorageCreateScheme(StorageScheme):
    pass


class StorageUpdateScheme(StorageScheme):
    pass


class DisplayBaseScheme(BaseModel):
    name: str
    refresh_rate_id: int
    display_size_id: int
    resolution_id: int
    display_type_id: int


class DisplayCreateScheme(BaseModel):
    name: str
    refresh_rate_values: List[int]  # List of refresh rate values
    display_size_values: List[float]  # List of display size values
    resolution_values: List[str]  # List of resolution values


class DisplayUpdateScheme(DisplayBaseScheme):
    refresh_rate_id: Optional[int] = None
    display_size_id: Optional[int] = None
    resolution_id: Optional[int] = None
    display_type_id: Optional[int] = None


class DisplayResponseScheme(DisplayBaseScheme):
    id: int

    
# Base schema for creating and updating processors
class ProcessorBaseScheme(BaseModel):
    name: str

    class Config:
        from_attributes = True


# Schema for creating a new processor
class ProcessorCreateScheme(ProcessorBaseScheme):
    pass


# Schema for updating an existing processor
class ProcessorUpdateScheme(ProcessorBaseScheme):
    pass


# Schema for the response of a single processor
class ProcessorResponseScheme(ProcessorBaseScheme):
    id: int

    class Config:
        from_attributes = True


# Schema for the response of a list of processors
class ProcessorListResponseScheme(BaseModel):
    items: list[ProcessorResponseScheme]


# Base schema for creating and updating gens
class GenBaseScheme(BaseModel):
    name: str
    processor_id: int

    class Config:
        from_attributes = True


# Schema for creating a new gen
class GenCreateScheme(GenBaseScheme):
    pass


# Schema for updating an existing gen
class GenUpdateScheme(GenBaseScheme):
    pass


# Schema for the response of a single gen
class GenResponseScheme(GenBaseScheme):
    id: int

    class Config:
        from_attributes = True


# Schema for the response of a list of gens
class GenListResponseScheme(BaseModel):
    items: list[GenResponseScheme]


class ComputerCreateScheme(BaseModel):
    name: str
    rams: List[int]
    storages: List[int]
    processors: List[int]
    displays: List[int]

    class Config:
        from_attributes = True


class ComputerResponseScheme(BaseModel):
    id: int
    name: str
    rams: List[int]
    storages: List[int]
    processors: List[int]
    displays: List[int]

    class Config:
        from_attributes = True
