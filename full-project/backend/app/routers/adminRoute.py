from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..repos.reviewRepo import loadReviews, saveReviews
from ..services.reviewService import deleteReview
from ..utilities.penalties import incrementPenaltyForUser
from ..schemas.user import CurrentUser
from .authRoute import requireAdmin
from ..schemas.admin import AdminFlagResponse, PaginatedFlaggedReviewsResponse
from ..schemas.review import Review
from ..services.adminService import grantAdmin, revokeAdmin, AdminActionError
from app.services.userService import UserNotFoundError

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------
# Helper functions
# ---------------------------


def getFlaggedReviews() -> List[Review]:
    reviewList = loadReviews()
    return [review for review in reviewList if review.flagged]


def getReviewById(reviewId: int):
    """Return full list and the review object for the given ID."""
    reviewList = loadReviews()
    review = next((review for review in reviewList if review.id == reviewId), None)
    if review is None:
        raise HTTPException(404, "Review not found")
    return reviewList, review


# ---------------------------
# Accept flag and delete review
# ---------------------------


@router.post("/reviews/{reviewId}/acceptFlag", response_model=AdminFlagResponse)
def acceptReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """Accept a review flag, delete the review, and penalize the user."""
    _, review = getReviewById(reviewId)

    # Penalize the user
    updatedUser = incrementPenaltyForUser(review.userId)

    # Delete the review
    deleteReview(reviewId)

    return AdminFlagResponse(
        message="Review flag accepted. Review deleted and user penalized.",
        userId=updatedUser.id,
        penaltyCount=updatedUser.penalties,
        isBanned=updatedUser.isBanned,
    )


# ---------------------------
# Reject flag
# ---------------------------


@router.post("/reviews/{reviewId}/rejectFlag", response_model=AdminFlagResponse)
def rejectReviewFlag(reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)):
    """Reject a review flag and unflag the review."""
    reviewList, review = getReviewById(reviewId)

    # Simply unflag the review
    review.flagged = False
    saveReviews(reviewList)

    # We can still return a user-like response with dummy values if needed
    return AdminFlagResponse(
        message="Flag rejected. Review unflagged (no penalty applied).",
        userId=review.userId,
        penaltyCount=0,
        isBanned=False,
    )


# ---------------------------
# Mark review inappropriate
# ---------------------------


@router.post("/reviews/{reviewId}/markInappropriate", response_model=AdminFlagResponse)
def markReviewInappropriate(
    reviewId: int, currentAdmin: CurrentUser = Depends(requireAdmin)
):
    """Mark a review as inappropriate and penalize the user."""
    reviewList, review = getReviewById(reviewId)

    reviewList = [review for review in reviewList if review.id != reviewId]
    saveReviews(reviewList)

    updatedUser = incrementPenaltyForUser(review.userId)

    return AdminFlagResponse(
        message="Review flagged and user penalized",
        userId=updatedUser.id,
        penaltyCount=updatedUser.penalties,
        isBanned=updatedUser.isBanned,
    )


# ---------------------------
# Paginated flagged review reports
# ---------------------------


@router.get("/reports/reviews", response_model=PaginatedFlaggedReviewsResponse)
def getFlaggedReviewReports(
    page: int = 1,
    pageSize: int = 20,
    currentAdmin: CurrentUser = Depends(requireAdmin),
):
    flaggedReviewList = getFlaggedReviews()

    startIndex = (page - 1) * pageSize
    endIndex = startIndex + pageSize
    paginatedReviews = flaggedReviewList[startIndex:endIndex]

    return PaginatedFlaggedReviewsResponse(
        page=page,
        pageSize=pageSize,
        totalFlagged=len(flaggedReviewList),
        pageCount=(len(flaggedReviewList) + pageSize - 1) // pageSize,
        reviews=paginatedReviews,
    )


@router.put("/{userId}/grantAdmin")
def grantAdminPrivileges(
    userId: int, currentAdmin: CurrentUser = Depends(requireAdmin)
):
    """Grant admin privileges to a user."""
    try:
        updatedUser = grantAdmin(userId, currentAdmin)
    except AdminActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "message": "Admin privileges granted.",
        "userId": updatedUser.id,
        "role": updatedUser.role,
    }


@router.put("/{userId}/revokeAdmin")
def revokeAdminPrivileges(
    userId: int, currentAdmin: CurrentUser = Depends(requireAdmin)
):
    """Revoke admin privileges from a user."""
    try:
        updatedUser = revokeAdmin(userId, currentAdmin)
    except AdminActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "message": "Admin privileges revoked.",
        "userId": updatedUser.id,
        "role": updatedUser.role,
    }
