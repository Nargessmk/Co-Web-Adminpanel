"""
Security questions service using FusionAuth SDK.

Stores and verifies security questions in FusionAuth user.data blob.
Mirrors the C# UserManagementService security question methods.
"""

from __future__ import annotations

import json
from typing import Any

from core.exceptions import FusionAuthAPIError, FusionAuthNotFoundError
from Schema.Authentication.auth import SecurityQuestionsRequest
from services.fusionauth_client import FusionAuthSDKClient, get_fusionauth_client

DATA_KEY = "securityQuestions"


class SecurityQuestionsService:

    def __init__(self, client: FusionAuthSDKClient | None = None) -> None:
        self._client = client or get_fusionauth_client()

    async def set_questions(self, user_id: str, model: SecurityQuestionsRequest) -> bool:
        user_data = await self._client.retrieve_user(user_id)
        user = user_data.get("user")
        if not user:
            return False

        data = user.get("data", {})
        data[DATA_KEY] = json.dumps({
            "Email": model.Email,
            "Questions": [{"QuestionId": q.QuestionId, "Answer": q.Answer} for q in model.Questions],
        })

        result = await self._client.update_user(user_id, {"user": {"data": data}})
        return "user" in result

    async def verify_questions(self, model: SecurityQuestionsRequest) -> str:
        user_data = await self._client.retrieve_user_by_email(model.Email)
        user = user_data.get("user")
        if not user:
            raise FusionAuthNotFoundError("User not found", status_code=404)

        user_data_blob = user.get("data", {})
        stored_json = user_data_blob.get(DATA_KEY)
        if not stored_json:
            raise FusionAuthAPIError("Security questions not configured", status_code=400)

        stored = json.loads(stored_json) if isinstance(stored_json, str) else stored_json
        stored_map = {q["QuestionId"]: q["Answer"] for q in stored.get("Questions", [])}

        for submitted in model.Questions:
            stored_answer = stored_map.get(submitted.QuestionId)
            if stored_answer is None:
                raise FusionAuthAPIError("Invalid security question", status_code=400)
            if stored_answer.lower() != submitted.Answer.lower():
                raise FusionAuthAPIError("Incorrect answer", status_code=400)

        fp_result = await self._client.forgot_password({
            "loginId": model.Email,
            "sendForgotPasswordEmail": False,
        })
        change_password_id = fp_result.get("changePasswordId", "")
        if not change_password_id:
            raise FusionAuthAPIError("Failed to generate change password token", status_code=500)

        return change_password_id

    async def get_questions(self, user_id: str) -> dict[str, Any] | None:
        user_data = await self._client.retrieve_user(user_id)
        user = user_data.get("user")
        if not user:
            return None
        stored_json = user.get("data", {}).get(DATA_KEY)
        if not stored_json:
            return None
        return json.loads(stored_json) if isinstance(stored_json, str) else stored_json


_security_questions_service: SecurityQuestionsService | None = None


def get_security_questions_service() -> SecurityQuestionsService:
    global _security_questions_service
    if _security_questions_service is None:
        _security_questions_service = SecurityQuestionsService()
    return _security_questions_service
