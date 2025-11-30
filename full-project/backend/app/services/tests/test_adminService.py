import pytest
from app.services import adminService
from app.schemas.user import User, CurrentUser, AdminUserUpdate
from app.schemas.role import Role


def makeUser(userId=1, role=Role.USER):
    return User(
        id=userId,
        username="user",
        firstName="First",
        lastName="Last",
        age=None,
        email="user@example.com",
        pw="hashed",
        role=role,
        penalties=0,
        isBanned=False,
        watchlist=[],
    )


def makeCurrentAdmin(adminId=1):
    return CurrentUser(
        id=adminId,
        username="admin",
        role=Role.ADMIN,
    )


def testGrantAdminCallsUpdateUserWithAdminRole(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    updatedUser = makeUser(userId=userId, role=Role.ADMIN)

    updateUserMock = mocker.patch(
        "app.services.adminService.updateUser",
        return_value=updatedUser,
    )

    result = adminService.grantAdmin(userId, currentAdmin)

    updateUserMock.assert_called_once()
    calledUserId, payload = updateUserMock.call_args.args
    assert calledUserId == userId
    assert isinstance(payload, AdminUserUpdate)
    assert payload.role == Role.ADMIN
    assert result == updatedUser


def testGrantAdminRaisesAdminActionErrorWhenTargetIsCurrentAdmin():
    currentAdmin = makeCurrentAdmin()
    with pytest.raises(adminService.AdminActionError):
        adminService.grantAdmin(currentAdmin.id, currentAdmin)


def testRevokeAdminCallsUpdateUserWithUserRole(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    updatedUser = makeUser(userId=userId, role=Role.USER)

    updateUserMock = mocker.patch(
        "app.services.adminService.updateUser",
        return_value=updatedUser,
    )

    with pytest.raises(adminService.AdminActionError):
        result = adminService.revokeAdmin(userId, currentAdmin)


def testRevokeAdminRaisesAdminActionErrorWhenTargetIsCurrentAdmin():
    currentAdmin = makeCurrentAdmin()
    with pytest.raises(adminService.AdminActionError):
        adminService.revokeAdmin(currentAdmin.id, currentAdmin)
