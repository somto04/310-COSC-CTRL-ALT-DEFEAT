from app.schemas.user import CurrentUser, User
from app.schemas.user import AdminUserUpdate
from app.schemas.role import Role
from app.services.userService import getUserById, updateUser


class AdminActionError(Exception):
    def __init__(self, message: str = "Admin action failed"):
        super().__init__(message)

def grantAdmin(userId: int, currentAdmin: CurrentUser) -> User:
    """Grant admin privileges to a user."""
    if currentAdmin.id == userId:
        raise AdminActionError("You are already an admin, silly")
    currentUser = getUserById(userId)
    if currentUser.role == Role.ADMIN:
        raise AdminActionError("User is already an admin")
    
    update = AdminUserUpdate(role=Role.ADMIN)
    updatedUser = updateUser(userId, update)
    return updatedUser
    

def revokeAdmin(userId: int, currentAdmin: CurrentUser) -> User:
    """Revoke admin privileges from a user."""
    if currentAdmin.id == userId:
        raise AdminActionError("Cannot revoke your own admin privileges")
    currentUser = getUserById(userId)
    if currentUser.role != Role.ADMIN:
        raise AdminActionError("User is not an admin")
    
    update = AdminUserUpdate(role=Role.USER)
    updatedUser = updateUser(userId, update)
    return updatedUser