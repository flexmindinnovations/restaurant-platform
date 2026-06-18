import uuid
from typing import Any

from fastapi import APIRouter, Depends, status

from modules.payments.api.dependencies import (
    get_add_payment_method_handler,
    get_list_payment_methods_handler,
    get_payment_query_handler,
    get_refund_payment_handler,
    get_remove_payment_method_handler,
)
from modules.payments.api.schemas import (
    AddPaymentMethodRequest,
    PaymentMethodResponse,
    PaymentResponse,
    RefundPaymentRequest,
)
from modules.payments.application.commands.add_payment_method import AddPaymentMethodCommand, AddPaymentMethodHandler
from modules.payments.application.commands.refund_payment import RefundPaymentCommand, RefundPaymentHandler
from modules.payments.application.commands.remove_payment_method import (
    RemovePaymentMethodCommand,
    RemovePaymentMethodHandler,
)
from modules.payments.application.queries.get_payment import GetPaymentByOrderHandler, GetPaymentByOrderQuery
from modules.payments.application.queries.list_payment_methods import (
    ListCustomerPaymentMethodsHandler,
    ListCustomerPaymentMethodsQuery,
)
from shared.api.response import ResponseEnvelope
from shared.api.security import get_current_user, require_roles

router = APIRouter()
admin_router = APIRouter()


# --- Customer Payment Methods ---


@router.post("/methods", response_model=ResponseEnvelope[PaymentMethodResponse], status_code=status.HTTP_201_CREATED)
async def add_payment_method(
    request: AddPaymentMethodRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: AddPaymentMethodHandler = Depends(get_add_payment_method_handler),
    query_handler: ListCustomerPaymentMethodsHandler = Depends(get_list_payment_methods_handler),
) -> ResponseEnvelope[PaymentMethodResponse]:
    customer_id = uuid.UUID(current_user["sub"])
    command = AddPaymentMethodCommand(
        customer_id=customer_id,
        type=request.type,
        last_four=request.last_four,
        brand=request.brand,
        is_default=request.is_default,
        token=request.token,
    )
    method_id = await handler.handle(command)

    # Fetch to return response
    dto_list = await query_handler.handle(ListCustomerPaymentMethodsQuery(customer_id=customer_id))
    method_dto = next(m for m in dto_list if m.id == method_id)
    return ResponseEnvelope(data=PaymentMethodResponse.model_validate(method_dto))


@router.get("/methods", response_model=ResponseEnvelope[list[PaymentMethodResponse]])
async def list_payment_methods(
    current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: ListCustomerPaymentMethodsHandler = Depends(get_list_payment_methods_handler),
) -> ResponseEnvelope[list[PaymentMethodResponse]]:
    customer_id = uuid.UUID(current_user["sub"])
    dtos = await query_handler.handle(ListCustomerPaymentMethodsQuery(customer_id=customer_id))
    return ResponseEnvelope(data=[PaymentMethodResponse.model_validate(dto) for dto in dtos])


@router.delete("/methods/{method_id}", response_model=ResponseEnvelope[dict])
async def remove_payment_method(
    method_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(get_current_user),
    handler: RemovePaymentMethodHandler = Depends(get_remove_payment_method_handler),
) -> ResponseEnvelope[dict]:
    customer_id = uuid.UUID(current_user["sub"])
    command = RemovePaymentMethodCommand(
        customer_id=customer_id,
        payment_method_id=method_id,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Payment method removed successfully"})


# --- Order Payments ---


@router.get("/orders/{order_id}", response_model=ResponseEnvelope[PaymentResponse])
async def get_order_payment(
    order_id: uuid.UUID,
    _current_user: dict[str, Any] = Depends(get_current_user),
    query_handler: GetPaymentByOrderHandler = Depends(get_payment_query_handler),
) -> ResponseEnvelope[PaymentResponse]:
    dto = await query_handler.handle(GetPaymentByOrderQuery(order_id=order_id))
    return ResponseEnvelope(data=PaymentResponse.model_validate(dto))


# --- Admin Refund Operations ---


@admin_router.post("/{payment_id}/refund", response_model=ResponseEnvelope[dict])
async def refund_payment(
    payment_id: uuid.UUID,
    request: RefundPaymentRequest,
    _current_user: dict[str, Any] = Depends(require_roles("SUPER_ADMIN")),
    handler: RefundPaymentHandler = Depends(get_refund_payment_handler),
) -> ResponseEnvelope[dict]:
    command = RefundPaymentCommand(
        payment_id=payment_id,
        amount=request.amount,
    )
    await handler.handle(command)
    return ResponseEnvelope(data={"message": "Payment refunded successfully"})
