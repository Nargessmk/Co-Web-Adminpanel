"""Tests for Pydantic schemas."""

from uuid import uuid4

from Schema.Authentication.auth import (
    AdminResetPasswordRequest,
    ChangePasswordRequest,
    ChangePasswordWithTokenRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordConfirmRequest,
    RoleInfo,
    RoleResult,
    SecurityQuestionAnswer,
    SecurityQuestionsRequest,
    TokenResponse,
    TwoFactorDisableRequest,
    TwoFactorLoginRequest,
    TwoFactorSecretResponse,
    TwoFactorSetupRequest,
    UserRemoveApplicationRequest,
    UserRolesAndGroups,
    UserRolesRequest,
)
from Schema.Authentication.user import (
    FusionAuthRegistrationResponse,
    FusionAuthUserResponse,
    GroupMembershipRequest,
    RoleAssignmentRequest,
    RoleRemovalRequest,
    UserCreateRequest,
    UserDetailResponse,
    UserListResponse,
    UserSearchRequest,
    UserProfileImageResponse,
    UserUpdateRequest,
)


class TestAuthSchemas:
    def test_login_request(self):
        m = LoginRequest(applicationId="a1", userName="u", password="p")
        assert m.applicationId == "a1"
        assert m.userName == "u"
        assert m.password == "p"

    def test_register_request(self):
        m = RegisterRequest(
            applicationId="a1", email="t@t.com", username="u", password="pass123"
        )
        assert m.email == "t@t.com"

    def test_token_response(self):
        m = TokenResponse(
            accessToken="at", refreshToken="rt", expiresIn=900,
            userId="u1", applicationId="a1"
        )
        assert m.tokenType == "Bearer"

    def test_change_password_request(self):
        m = ChangePasswordRequest(id="u1", currentPassword="old", password="new")
        assert m.id == "u1"

    def test_change_password_with_token_request(self):
        m = ChangePasswordWithTokenRequest(
            id="u1", changePasswordId="tok", currentPassword="old", password="new"
        )
        assert m.changePasswordId == "tok"

    def test_admin_reset_password_request(self):
        m = AdminResetPasswordRequest(Id=uuid4(), Email="t@t.com")
        assert m.newPassword is None

    def test_forgot_password_request(self):
        m = ForgotPasswordRequest(applicationId="a1", email="t@t.com")
        assert m.email == "t@t.com"

    def test_security_question_answer(self):
        m = SecurityQuestionAnswer(QuestionId=1, Answer="test")
        assert m.QuestionId == 1

    def test_security_questions_request(self):
        q = SecurityQuestionAnswer(QuestionId=1, Answer="a")
        m = SecurityQuestionsRequest(Email="t@t.com", Questions=[q])
        assert len(m.Questions) == 1

    def test_two_factor_login_request(self):
        m = TwoFactorLoginRequest(
            applicationId=uuid4(), userId=uuid4(), code="123456"
        )
        assert len(m.code) == 6

    def test_two_factor_disable_request(self):
        m = TwoFactorDisableRequest(UserId=uuid4(), Code="123456")
        assert m.Code == "123456"

    def test_user_roles_request(self):
        m = UserRolesRequest(UserId=uuid4(), ApplicationId=uuid4(), Roles=["admin"])
        assert len(m.Roles) == 1

    def test_role_info(self):
        m = RoleInfo(Name="admin")
        assert m.Name == "admin"
        assert m.Id is None

    def test_token_refresh_request(self):
        m = RefreshTokenRequest(refreshToken="rt123")
        assert m.refreshToken == "rt123"


class TestUserSchemas:
    def test_user_create_request(self):
        m = UserCreateRequest(
            username="test", email="t@t.com", password="pass12345", applicationId="a1"
        )
        assert m.username == "test"

    def test_user_update_request(self):
        m = UserUpdateRequest(firstName="John")
        assert m.firstName == "John"
        assert m.email is None

    def test_user_search_request(self):
        m = UserSearchRequest(query="test", pageIndex=0, pageSize=25)
        assert m.pageSize == 25

    def test_user_list_response(self):
        m = UserListResponse(users=[], total=0)
        assert m.total == 0

    def test_user_detail_response(self):
        m = UserDetailResponse(
            user=FusionAuthUserResponse(id="u1", email="t@t.com")
        )
        assert m.user.id == "u1"

    def test_role_assignment_request(self):
        m = RoleAssignmentRequest(userId="u1", applicationId="a1", roles=["admin"])
        assert len(m.roles) == 1

    def test_role_removal_request(self):
        m = RoleRemovalRequest(userId="u1", applicationId="a1", roles=["admin"])
        assert m.roles == ["admin"]

    def test_group_membership_request(self):
        m = GroupMembershipRequest(userId="u1", groupIds=["g1", "g2"])
        assert len(m.groupIds) == 2

    def test_user_profile_image_response(self):
        m = UserProfileImageResponse(success=True, imageUrl="/img.jpg")
        assert m.success is True

    def test_fusion_auth_user_response(self):
        m = FusionAuthUserResponse(id="u1", email="t@t.com", active=True)
        assert m.active is True
