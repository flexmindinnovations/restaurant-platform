from fastapi import APIRouter, Depends, status

from modules.identity.api.dependencies import (
    get_auth_service,
    get_forgot_password_handler,
    get_register_handler,
    get_reset_password_handler,
)
from modules.identity.api.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from modules.identity.application.commands.forgot_password import ForgotPasswordCommand, ForgotPasswordHandler
from modules.identity.application.commands.login import LoginCommand
from modules.identity.application.commands.refresh_token import RefreshTokenCommand
from modules.identity.application.commands.register_account import RegisterAccountCommand, RegisterAccountHandler
from modules.identity.application.commands.reset_password import ResetPasswordCommand, ResetPasswordHandler
from modules.identity.application.commands.verify_email import VerifyEmailCommand
from modules.identity.application.services.auth_service import AuthService
from shared.api.response import ResponseEnvelope

router = APIRouter()


@router.post(
    "/register",
    response_model=ResponseEnvelope[RegisterResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    handler: RegisterAccountHandler = Depends(get_register_handler),
) -> ResponseEnvelope[RegisterResponse]:
    command = RegisterAccountCommand(
        email=request.email,
        password=request.password,
        phone_number=request.phone_number,
        roles=request.roles,
    )
    account_id = await handler.handle(command)
    return ResponseEnvelope(data=RegisterResponse(id=account_id))


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    request: VerifyEmailRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    command = VerifyEmailCommand(email=request.email, token=request.token)
    await auth_service.verify_email(command)
    return {"data": {"message": "Email verified successfully"}}


@router.post("/login", response_model=ResponseEnvelope[LoginResponse], status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ResponseEnvelope[LoginResponse]:
    command = LoginCommand(email=request.email, password=request.password)
    res = await auth_service.login(command)
    return ResponseEnvelope(
        data=LoginResponse(
            access_token=res.access_token,
            refresh_token=res.refresh_token,
            token_type=res.token_type,
        )
    )


@router.post("/refresh", response_model=ResponseEnvelope[LoginResponse], status_code=status.HTTP_200_OK)
async def refresh(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ResponseEnvelope[LoginResponse]:
    command = RefreshTokenCommand(refresh_token=request.refresh_token)
    res = await auth_service.refresh_token(command)
    return ResponseEnvelope(
        data=LoginResponse(
            access_token=res.access_token,
            refresh_token=res.refresh_token,
            token_type=res.token_type,
        )
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    handler: ForgotPasswordHandler = Depends(get_forgot_password_handler),
) -> dict:
    command = ForgotPasswordCommand(email=request.email)
    await handler.handle(command)
    return {"data": {"message": "If the email is registered, a password reset link has been sent."}}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: ResetPasswordRequest,
    handler: ResetPasswordHandler = Depends(get_reset_password_handler),
) -> dict:
    command = ResetPasswordCommand(token=request.token, new_password=request.new_password)
    await handler.handle(command)
    return {"data": {"message": "Password reset successfully"}}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    await auth_service.logout(request.refresh_token)
    return {"data": {"message": "Logged out successfully"}}
