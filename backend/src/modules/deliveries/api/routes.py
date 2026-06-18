import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, status

from app.dependencies import get_db_session
from modules.deliveries.api.dependencies import (
    get_accept_assignment_handler,
    get_assign_partner_handler,
    get_delivery_by_order_query_handler,
    get_delivery_query_handler,
    get_list_partner_deliveries_handler,
    get_partner_location_handler,
    get_register_partner_handler,
    get_toggle_partner_availability_handler,
    get_toggle_partner_online_handler,
    get_update_delivery_status_handler,
    get_update_partner_location_handler,
)
from modules.deliveries.api.schemas import (
    AssignPartnerRequest,
    DeliveryResponse,
    PartnerLocationResponse,
    RegisterPartnerRequest,
    ToggleAvailabilityRequest,
    ToggleOnlineRequest,
    UpdateDeliveryStatusRequest,
    UpdatePartnerLocationRequest,
)
from modules.deliveries.application.commands.accept_assignment import AcceptAssignmentCommand, AcceptAssignmentHandler
from modules.deliveries.application.commands.assign_partner import AssignPartnerCommand, AssignPartnerHandler
from modules.deliveries.application.commands.register_partner import RegisterPartnerCommand, RegisterPartnerHandler
from modules.deliveries.application.commands.toggle_partner_availability import (
    TogglePartnerAvailabilityCommand,
    TogglePartnerAvailabilityHandler,
)
from modules.deliveries.application.commands.toggle_partner_online import (
    TogglePartnerOnlineCommand,
    TogglePartnerOnlineHandler,
)
from modules.deliveries.application.commands.update_delivery_status import (
    UpdateDeliveryStatusCommand,
    UpdateDeliveryStatusHandler,
)
from modules.deliveries.application.commands.update_partner_location import (
    UpdatePartnerLocationCommand,
    UpdatePartnerLocationHandler,
)
from modules.deliveries.application.queries.get_delivery import (
    GetDeliveryByOrderHandler,
    GetDeliveryByOrderQuery,
    GetDeliveryHandler,
    GetDeliveryQuery,
)
from modules.deliveries.application.queries.get_partner_location import (
    GetPartnerLocationHandler,
    GetPartnerLocationQuery,
)
from modules.deliveries.application.queries.list_partner_deliveries import (
    ListPartnerDeliveriesHandler,
    ListPartnerDeliveriesQuery,
)
from modules.deliveries.domain.value_objects.delivery_status import DeliveryStatus
from modules.deliveries.domain.value_objects.location import GeoLocation
from modules.deliveries.domain.value_objects.vehicle_type import VehicleType
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_roles
from shared.domain.exceptions import ValidationException

router = APIRouter()
partners_router = APIRouter()


# --- Partner Operations ---

@partners_router.post("/register", response_model=ResponseEnvelope[uuid.UUID], status_code=status.HTTP_201_CREATED)
async def register_partner(
    request: RegisterPartnerRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: RegisterPartnerHandler = Depends(get_register_partner_handler),
) -> ResponseEnvelope[uuid.UUID]:
    account_id = uuid.UUID(current_user["sub"])
    command = RegisterPartnerCommand(
        account_id=account_id,
        name=request.name,
        phone=request.phone,
        vehicle_type=VehicleType(request.vehicle_type),
    )
    partner_id = await handler.handle(command)
    return ResponseEnvelope(data=partner_id)


@partners_router.post("/{partner_id}/online", response_model=ResponseEnvelope[dict])
async def toggle_online(
    partner_id: uuid.UUID,
    request: ToggleOnlineRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: TogglePartnerOnlineHandler = Depends(get_toggle_partner_online_handler),
) -> ResponseEnvelope[dict]:
    await handler.handle(TogglePartnerOnlineCommand(partner_id=partner_id, is_online=request.is_online))
    status_msg = "online" if request.is_online else "offline"
    return ResponseEnvelope(data={"message": f"Partner is now {status_msg}"})


@partners_router.post("/{partner_id}/availability", response_model=ResponseEnvelope[dict])
async def toggle_availability(
    partner_id: uuid.UUID,
    request: ToggleAvailabilityRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: TogglePartnerAvailabilityHandler = Depends(get_toggle_partner_availability_handler),
) -> ResponseEnvelope[dict]:
    await handler.handle(TogglePartnerAvailabilityCommand(partner_id=partner_id, is_available=request.is_available))
    status_msg = "available" if request.is_available else "unavailable"
    return ResponseEnvelope(data={"message": f"Partner availability is now {status_msg}"})


@partners_router.post("/{partner_id}/location", response_model=ResponseEnvelope[dict])
async def update_location(
    partner_id: uuid.UUID,
    request: UpdatePartnerLocationRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: UpdatePartnerLocationHandler = Depends(get_update_partner_location_handler),
) -> ResponseEnvelope[dict]:
    command = UpdatePartnerLocationCommand(
        partner_id=partner_id,
        location=GeoLocation(latitude=request.latitude, longitude=request.longitude),
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Location updated successfully"})


@partners_router.get("/{partner_id}/location", response_model=ResponseEnvelope[PartnerLocationResponse])
async def get_partner_location(
    partner_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: GetPartnerLocationHandler = Depends(get_partner_location_handler),
) -> ResponseEnvelope[PartnerLocationResponse]:
    dto = await handler.handle(GetPartnerLocationQuery(partner_id=partner_id))
    return ResponseEnvelope(
        data=PartnerLocationResponse(
            partner_id=dto.partner_id,
            latitude=dto.latitude,
            longitude=dto.longitude,
        )
    )


@partners_router.get("/{partner_id}/deliveries", response_model=ResponseEnvelope[list[DeliveryResponse]])
async def list_partner_deliveries(
    partner_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: ListPartnerDeliveriesHandler = Depends(get_list_partner_deliveries_handler),
) -> ResponseEnvelope[list[DeliveryResponse]]:
    dtos = await handler.handle(ListPartnerDeliveriesQuery(partner_id=partner_id))
    return ResponseEnvelope(data=[DeliveryResponse.model_validate(dto) for dto in dtos])


# --- Delivery Operations ---

@router.get("/{delivery_id}", response_model=ResponseEnvelope[DeliveryResponse])
async def get_delivery(
    delivery_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: GetDeliveryHandler = Depends(get_delivery_query_handler),
) -> ResponseEnvelope[DeliveryResponse]:
    dto = await handler.handle(GetDeliveryQuery(delivery_id=delivery_id))
    return ResponseEnvelope(data=DeliveryResponse.model_validate(dto))


@router.get("/orders/{order_id}", response_model=ResponseEnvelope[DeliveryResponse])
async def get_delivery_by_order(
    order_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: GetDeliveryByOrderHandler = Depends(get_delivery_by_order_query_handler),
) -> ResponseEnvelope[DeliveryResponse]:
    dto = await handler.handle(GetDeliveryByOrderQuery(order_id=order_id))
    return ResponseEnvelope(data=DeliveryResponse.model_validate(dto))


@router.post("/{delivery_id}/accept", response_model=ResponseEnvelope[dict])
async def accept_delivery(
    delivery_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: AcceptAssignmentHandler = Depends(get_accept_assignment_handler),
    session=Depends(get_db_session),
) -> ResponseEnvelope[dict]:
    # Lookup partner by current user account id
    from modules.deliveries.infrastructure.repositories.sqlalchemy_partner_repository import SqlAlchemyPartnerRepository
    partner_repo = SqlAlchemyPartnerRepository(session)
    account_id = uuid.UUID(_current_user["sub"])
    partner = await partner_repo.get_by_account_id(account_id)
    if not partner:
        raise ValidationException("Current user is not registered as a delivery partner")

    await handler.handle(AcceptAssignmentCommand(delivery_id=delivery_id, partner_id=partner.id))
    return ResponseEnvelope(data={"message": "Delivery assignment accepted"})


@router.post("/{delivery_id}/status", response_model=ResponseEnvelope[dict])
async def update_delivery_status(
    delivery_id: uuid.UUID,
    request: UpdateDeliveryStatusRequest,
    _current_user: dict[str, Any] = Depends(get_current_user),
    handler: UpdateDeliveryStatusHandler = Depends(get_update_delivery_status_handler),
    session=Depends(get_db_session),
) -> ResponseEnvelope[dict]:
    # Lookup partner by current user account id
    from modules.deliveries.infrastructure.repositories.sqlalchemy_partner_repository import SqlAlchemyPartnerRepository
    partner_repo = SqlAlchemyPartnerRepository(session)
    account_id = uuid.UUID(_current_user["sub"])
    partner = await partner_repo.get_by_account_id(account_id)
    if not partner:
        raise ValidationException("Current user is not registered as a delivery partner")

    command = UpdateDeliveryStatusCommand(
        delivery_id=delivery_id,
        partner_id=partner.id,
        status=DeliveryStatus(request.status),
        proof_of_delivery_url=request.proof_of_delivery_url,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": f"Delivery status updated to {request.status}"})


@router.post("/{delivery_id}/assign", response_model=ResponseEnvelope[dict])
async def trigger_assign_partner(
    delivery_id: uuid.UUID,
    request: AssignPartnerRequest,
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: AssignPartnerHandler = Depends(get_assign_partner_handler),
) -> ResponseEnvelope[dict]:
    initial = request.initial_radius_km if request.initial_radius_km is not None else 5.0
    maximum = request.max_radius_km if request.max_radius_km is not None else 15.0
    command = AssignPartnerCommand(
        delivery_id=delivery_id,
        initial_radius_km=Decimal(str(initial)),
        max_radius_km=Decimal(str(maximum)),
    )
    partner_id = await handler.handle(command)
    if not partner_id:
        return ResponseEnvelope(
            data={"message": "No partner could be assigned within max radius"},
        )
    return ResponseEnvelope(
        data={"message": f"Delivery assigned to partner {partner_id}"},
    )
