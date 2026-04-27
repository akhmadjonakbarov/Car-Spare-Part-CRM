from sqladmin import ModelView
from .models import (
    Computer,
    Ram,
    Rom,
    Processor,
    Gen,
    Display,
    DSize,
    Resolution,
    RefreshRate,
)


class ComputerAdmin(ModelView, model=Computer):
    column_list = [
        Computer.id,
        Computer.name,
        Computer.category_id,
        Computer.company_id,
    ]
    column_searchable_list = [Computer.name]
    name = "Computer"
    icon = "fa-solid fa-laptop"


class RamAdmin(ModelView, model=Ram):
    column_list = [Ram.id, Ram.size]
    name = "Ram"
    icon = "fa-solid fa-memory"


class RomAdmin(ModelView, model=Rom):
    column_list = [Rom.id, Rom.size, Rom.disk]
    name = "Rom"
    icon = "fa-solid fa-hdd"


class ProcessorAdmin(ModelView, model=Processor):
    column_list = [Processor.id, Processor.name]
    column_searchable_list = [Processor.name]
    name = "Processor"
    icon = "fa-solid fa-microchip"


class GenAdmin(ModelView, model=Gen):
    column_list = [Gen.id, Gen.name, Gen.processor_id]
    column_searchable_list = [Gen.name]
    name = "Generation"
    icon = "fa-solid fa-code-branch"


class DisplayAdmin(ModelView, model=Display):
    column_list = [Display.id, Display.name]
    column_searchable_list = [Display.name]
    name = "Display"
    icon = "fa-solid fa-desktop"


class DSizeAdmin(ModelView, model=DSize):
    column_list = [DSize.id, DSize.value]
    name = "Display Size"
    icon = "fa-solid fa-ruler-horizontal"


class ResolutionAdmin(ModelView, model=Resolution):
    column_list = [Resolution.id, Resolution.value]
    name = "Resolution"
    icon = "fa-solid fa-expand"


class RefreshRateAdmin(ModelView, model=RefreshRate):
    column_list = [RefreshRate.id, RefreshRate.value]
    name = "Refresh Rate"
    icon = "fa-solid fa-tachometer-alt"
