from fastapi import APIRouter, HTTPException, status, Depends
from apps.computer.models import Display, RefreshRate, DSize, DisplayRefreshRate, DisplayDSize, DisplayResolution, \
    Resolution
from apps.computer.routes.schemes import DisplayUpdateScheme, DisplayCreateScheme
from apps.computer.routes.serializers.display_serializer import DisplaySerializer
from di.db import db_dependency

from utils.response_type import response_list, response_item
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/displays",
    tags=["Display Management"],
)


# Endpoint to get all displays
@router.get("/all", status_code=status.HTTP_200_OK)
async def get_displays(db: db_dependency):
    try:
        serializer = DisplaySerializer(many=True)
        displays = db.query(Display).all()

        return response_list(lst=serializer.dump(displays))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_display(display: DisplayCreateScheme, db: db_dependency):
    try:
        with db.begin():
            existing_display = db.query(Display).filter_by(name=display.name).first()
            if not existing_display:
                existing_display = Display(
                    name=display.name,
                )
                db.add(existing_display)
                db.flush()

            # Handle refresh_rate
            for refresh_rate in display.refresh_rate_values:
                existing_rate = db.query(RefreshRate).filter_by(value=refresh_rate).first()
                if not existing_rate:
                    # Create new refresh rate if it doesn't exist
                    existing_rate = RefreshRate(value=refresh_rate)
                    db.add(existing_rate)
                    db.flush()
                    new_display_refresh_rate = DisplayRefreshRate(
                        display_id=existing_display.id,
                        refresh_rate_id=existing_rate.id
                    )
                    db.add(new_display_refresh_rate)
                    db.flush()
                else:
                    new_display_refresh_rate = DisplayRefreshRate(
                        display_id=existing_display.id,
                        refresh_rate_id=existing_rate.id
                    )
                    db.add(new_display_refresh_rate)
                    db.flush()

            # Handle display_size
            for display_size in display.display_size_values:
                existing_display_size = db.query(DSize).filter_by(value=display_size).first()
                if not existing_display_size:
                    # Create new display size if it doesn't exist
                    existing_display_size = DSize(value=display_size)
                    db.add(existing_display_size)
                    db.flush()
                    new_display_d_size = DisplayDSize(
                        display_id=existing_display.id,
                        dsize_id=existing_display_size.id
                    )
                    db.add(new_display_d_size)
                    db.flush()
                else:
                    new_display_d_size = DisplayDSize(
                        display_id=existing_display.id,
                        dsize_id=existing_display_size.id
                    )
                    db.add(new_display_d_size)
                    db.flush()

            # Handle resolution
            for resolution in display.resolution_values:
                existing_resolution = db.query(Resolution).filter_by(value=resolution).first()
                if not existing_resolution:
                    # Create new resolution if it doesn't exist
                    existing_resolution = Resolution(value=resolution)
                    db.add(existing_resolution)
                    db.flush()
                    new_display_resolution = DisplayResolution(
                        display_id=existing_display.id,
                        resolution_id=existing_resolution.id
                    )
                    db.add(new_display_resolution)
                    db.flush()
                else:
                    new_display_resolution = DisplayResolution(
                        display_id=existing_display.id,
                        resolution_id=existing_resolution.id
                    )
                    db.add(new_display_resolution)
                    db.flush()

        return response_item(item=existing_display)




    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Endpoint to update an existing display
@router.patch("/update/{display_id}", status_code=status.HTTP_200_OK)
async def update_display(display_id: int, display: DisplayUpdateScheme, db: db_dependency):
    try:
        existing_display = db.query(Display).filter(Display.id == display_id).first()
        if not existing_display:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Display not found",
            )

        if display.refresh_rate_id is not None:
            existing_display.refresh_rate_id = display.refresh_rate_id
        if display.display_size_id is not None:
            existing_display.display_size_id = display.display_size_id
        if display.resolution_id is not None:
            existing_display.resolution_id = display.resolution_id
        if display.display_type_id is not None:
            existing_display.display_type_id = display.display_type_id

        db.commit()
        db.refresh(existing_display)
        return response_item(item=existing_display)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# Endpoint to delete a display
@router.delete("/delete/{display_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_display(display_id: int, db: db_dependency):
    try:
        display_to_delete = db.query(Display).filter(Display.id == display_id).first()
        if not display_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Display not found",
            )
        db.delete(display_to_delete)
        db.commit()
        return {"detail": "Display deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
