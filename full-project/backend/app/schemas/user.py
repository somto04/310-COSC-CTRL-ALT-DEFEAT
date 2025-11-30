from pydantic import (
    BaseModel,
    Field,
    field_validator,
    StringConstraints,
    AliasChoices,
)
from typing import Annotated, Optional, List
from .role import Role
import re
from pydantic.functional_validators import AfterValidator

MAX_NAME_LENGTH = 50
MIN_EMAIL_LENGTH = 5
MAX_EMAIL_LENGTH = 254
MIN_AGE = 16
MAX_AGE = 120
PASSWORD_RE = re.compile(r"^(?=\S*[A-Z])(?=\S*[a-z])(?=\S*\d)\S+$")
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 30
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 256


def _checkPasswordComplexity(value: str) -> str:
    """
    Extra password complexity check:
    - at least one uppercase
    - at least one lowercase
    - at least one digit
    """
    if not PASSWORD_RE.match(value):
        raise ValueError(
            "Password must contain at least one uppercase, one lowercase, and one digit"
        )
    return value


Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_USERNAME_LENGTH,
        max_length=MAX_USERNAME_LENGTH,
        pattern=r"^[A-Za-z0-9_.-]+$",
    ),
    
]
Password = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_PASSWORD_LENGTH,
        max_length=MAX_PASSWORD_LENGTH,
    ),
    AfterValidator(_checkPasswordComplexity),
]
Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_EMAIL_LENGTH,
        max_length=MAX_EMAIL_LENGTH,
        pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    ),
]
NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=MAX_NAME_LENGTH,
    ),
]


class User(BaseModel):
    """
    Schema representing a user in the system.

    Loose validation to accommodate legacy data.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username as stored; may not follow current validation rules.
        firstName (str): First name; may be empty for legacy users.
        lastName (str): Last name; may be empty for legacy users.
        age (Optional[int]): User's age.
        email (str): User's validated email address; legacy users may have empty email.
        pw (str): Hashed password; legacy users may have empty password.
        role (Role): Role of the user in the system.
        penalties (int): Number of penalties assigned to the user.
        isBanned (bool): Indicates if the user is banned.
    """

    id: int
    username: str
    firstName: str
    lastName: str
    age: Optional[int]
    email: str
    pw: str
    role: Role = Role.USER
    penalties: int = Field(
        default=0, validation_alias=AliasChoices("penaltyCount", "penalties")
    )
    isBanned: bool = False
    likedReviews: Optional[list[int]] = Field(default_factory=list)
    watchlist: List[int] = Field(default_factory=list)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Only exposes necessary fields for user creation.

    Attributes:
        username (Username): Unique username following defined constraints.
        firstName (NameStr): User's first name.
        lastName (NameStr): User's last name.
        age (int): User's age.
        email (Email): User's validated email address.
        pw (Password): Password following defined constraints.
    """

    username: Username = Field(
        ...,
        description=f"Username containing only letters, numbers, and _.-, and {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters",
    )
    firstName: NameStr = Field(
        ...,
        description=f"First name having non-whitespace characters and 1-{MAX_NAME_LENGTH} characters",
    )
    lastName: NameStr = Field(
        ...,
        description=f"Last name having non-whitespace characters and 1-{MAX_NAME_LENGTH} characters",
    )
    age: int = Field(
        ...,
        ge=MIN_AGE,
        le=MAX_AGE,
        description=f"User must be {MIN_AGE} years or older",
    )
    email: Email = Field(..., description="User's email address")
    pw: Password = Field(
        ...,
        description=f"Password with at least one uppercase letter, one lowercase letter, one digit, and {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters",
    )
    

    @field_validator("age")
    @classmethod
    def checkAge(cls, userAge):
        if userAge < MIN_AGE:
            raise ValueError(
                f"User must be {MIN_AGE} years or older to create an account"
            )
        return userAge


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    All fields are optional to allow partial updates.

    Attributes:
        username (Optional[Username]): Unique username for the user.
        firstName (Optional[NameStr]): User's first name.
        lastName (Optional[NameStr]): User's last name.
        age (Optional[int]): User's age.
        email (Optional[Email]): User's email address.
        pw (Optional[Password]): Password for the user account.
    """

    username: Optional[Username] = Field(
        default=None,
        description=f"Username containing only letters, numbers, and _.-, and {MIN_USERNAME_LENGTH}-{MAX_USERNAME_LENGTH} characters",
    )
    firstName: Optional[NameStr] = Field(
        default=None,
        description=f"First name having non-whitespace characters and 1-{MAX_NAME_LENGTH} characters",
    )
    lastName: Optional[NameStr] = Field(
        default=None,
        description=f"Last name having non-whitespace characters and 1-{MAX_NAME_LENGTH} characters",
    )
    age: Optional[int] = Field(
        default=None,
        ge=MIN_AGE,
        le=MAX_AGE,
        description=f"User must be {MIN_AGE} years or older",
    )
    email: Optional[Email] = Field(default=None, description="User's email address")
    pw: Optional[Password] = Field(
        default=None,
        description=f"Password with at least one uppercase letter, one lowercase letter, one digit, and {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters",
    )
    watchlist: Optional[List[int]] = Field(default_factory=list, description="User's watch list")

    @field_validator("age")
    @classmethod
    def checkAge(cls, userAge):
        if userAge is not None and userAge < MIN_AGE:
            raise ValueError(
                f"User must be {MIN_AGE} years or older to update an account"
            )
        return userAge


class AdminUserUpdate(UserUpdate):
    """
    Schema for updating user information by an admin.

    Inherits from UserUpdate and allows modification of all fields, including role, penalties, and ban status.
    Only exposes fields that an admin can update.

    Attributes:
        ... from UserUpdate
        role (Optional[Role]): Role of the user in the system.
        penalties (Optional[int]): Number of penalties assigned to the user.
        isBanned (Optional[bool]): Indicates if the user is banned.
    """

    role: Optional[Role] = Field(
        default=None, description="Role of the user in the system, e.g., USER or ADMIN"
    )
    penalties: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("penaltyCount", "penalties"),
        description="Number of penalties assigned to the user, 3 is the max.",
    )
    isBanned: Optional[bool] = None


class CurrentUser(BaseModel):
    """
    Schema representing the currently authenticated user.

    Only exposes non-sensitive information.

    Attributes:
        id (int): Unique identifier for the user.
        username (Username): Unique username following defined constraints.
        role (Role): Role of the user in the system.
    """

    id: int
    username: Username
    role: Role

class SafeUser(BaseModel):
    id: int
    username: str
    firstName: str
    isBanned: bool
    watchlist: List[int]
