import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from modules.reviews.application.commands.flag_review import FlagReviewCommand, FlagReviewHandler
from modules.reviews.application.commands.reply_to_review import ReplyToReviewCommand, ReplyToReviewHandler
from modules.reviews.application.commands.submit_review import SubmitReviewCommand, SubmitReviewHandler
from modules.reviews.application.commands.update_review import UpdateReviewCommand, UpdateReviewHandler
from modules.reviews.domain.entities.review import Review
from modules.reviews.domain.value_objects.review_rating import ReviewRating
from modules.reviews.domain.value_objects.sentiment import Sentiment
from shared.domain.exceptions import NotFoundException, ValidationException

# --- Domain: ReviewRating ---


@pytest.mark.unit
def test_review_rating_valid():
    for value in range(1, 6):
        rating = ReviewRating(value=value)
        assert rating.value == value


@pytest.mark.unit
def test_review_rating_invalid_zero():
    with pytest.raises(ValidationException, match="between 1 and 5"):
        ReviewRating(value=0)


@pytest.mark.unit
def test_review_rating_invalid_six():
    with pytest.raises(ValidationException, match="between 1 and 5"):
        ReviewRating(value=6)


@pytest.mark.unit
def test_review_rating_invalid_negative():
    with pytest.raises(ValidationException, match="between 1 and 5"):
        ReviewRating(value=-1)


# --- Domain: Sentiment ---


@pytest.mark.unit
def test_sentiment_values():
    assert Sentiment.POSITIVE == "POSITIVE"
    assert Sentiment.NEUTRAL == "NEUTRAL"
    assert Sentiment.NEGATIVE == "NEGATIVE"


# --- Domain: Review entity ---


def _make_review(**kwargs):
    defaults = {
        "order_id": uuid.uuid4(),
        "customer_id": uuid.uuid4(),
        "restaurant_id": uuid.uuid4(),
        "rating": 4,
        "comment": "Great food!",
    }
    defaults.update(kwargs)
    return Review.submit(**defaults)


@pytest.mark.unit
def test_review_submit():
    order_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    restaurant_id = uuid.uuid4()

    review = Review.submit(
        order_id=order_id,
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        rating=5,
        comment="Excellent!",
        images=["img1.jpg", "img2.jpg"],
    )

    assert review.order_id == order_id
    assert review.customer_id == customer_id
    assert review.restaurant_id == restaurant_id
    assert review.rating.value == 5
    assert review.comment == "Excellent!"
    assert review.images == ["img1.jpg", "img2.jpg"]
    assert review.is_flagged is False
    assert review.reply is None
    assert review.sentiment is None
    assert len(review.collect_events()) == 1


@pytest.mark.unit
def test_review_submit_invalid_rating():
    with pytest.raises(ValidationException, match="between 1 and 5"):
        Review.submit(
            order_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            rating=0,
        )


@pytest.mark.unit
def test_review_submit_too_many_images():
    with pytest.raises(ValidationException, match="Maximum 5 images"):
        Review.submit(
            order_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            rating=4,
            images=["a", "b", "c", "d", "e", "f"],
        )


@pytest.mark.unit
def test_review_submit_comment_too_long():
    with pytest.raises(ValidationException, match="2000 characters"):
        Review.submit(
            order_id=uuid.uuid4(),
            customer_id=uuid.uuid4(),
            restaurant_id=uuid.uuid4(),
            rating=4,
            comment="x" * 2001,
        )


@pytest.mark.unit
def test_review_update_within_window():
    review = _make_review()
    review.collect_events()

    review.update(rating=3, comment="Updated")
    assert review.rating.value == 3
    assert review.comment == "Updated"
    events = review.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "ReviewUpdated"


@pytest.mark.unit
def test_review_update_outside_window():
    review = _make_review()
    review.created_at = datetime.now(UTC) - timedelta(hours=49)

    with pytest.raises(ValidationException, match="48 hours"):
        review.update(rating=2)


@pytest.mark.unit
def test_review_is_editable():
    review = _make_review()
    assert review.is_editable is True

    review.created_at = datetime.now(UTC) - timedelta(hours=49)
    assert review.is_editable is False


@pytest.mark.unit
def test_review_add_reply():
    review = _make_review()
    review.collect_events()

    review.add_reply("Thank you for your feedback!")
    assert review.reply == "Thank you for your feedback!"
    assert review.replied_at is not None
    events = review.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "ReviewReplied"


@pytest.mark.unit
def test_review_add_reply_empty():
    review = _make_review()
    with pytest.raises(ValidationException, match="Reply cannot be empty"):
        review.add_reply("")


@pytest.mark.unit
def test_review_add_reply_too_long():
    review = _make_review()
    with pytest.raises(ValidationException, match="1000 characters"):
        review.add_reply("x" * 1001)


@pytest.mark.unit
def test_review_flag():
    review = _make_review()
    review.collect_events()

    review.flag("Inappropriate content")
    assert review.is_flagged is True
    assert review.flag_reason == "Inappropriate content"
    events = review.collect_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "ReviewFlagged"


@pytest.mark.unit
def test_review_flag_empty_reason():
    review = _make_review()
    with pytest.raises(ValidationException, match="Flag reason is required"):
        review.flag("")


@pytest.mark.unit
def test_review_unflag():
    review = _make_review()
    review.flag("test")
    assert review.is_flagged is True

    review.unflag()
    assert review.is_flagged is False
    assert review.flag_reason is None


# --- Application: SubmitReviewHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_submit_review_handler_success():
    review_repo = AsyncMock()
    review_repo.get_by_order_id.return_value = None

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = SubmitReviewHandler(review_repo, uow)
    command = SubmitReviewCommand(
        order_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        restaurant_id=uuid.uuid4(),
        rating=5,
        comment="Amazing!",
    )

    review_id = await handler.handle(command)
    assert review_id is not None
    review_repo.add.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_submit_review_handler_duplicate_order():
    review_repo = AsyncMock()
    review_repo.get_by_order_id.return_value = _make_review()

    uow = AsyncMock()
    handler = SubmitReviewHandler(review_repo, uow)
    command = SubmitReviewCommand(
        order_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        restaurant_id=uuid.uuid4(),
        rating=5,
    )

    with pytest.raises(ValidationException, match="already exists"):
        await handler.handle(command)


# --- Application: UpdateReviewHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_review_handler_success():
    customer_id = uuid.uuid4()
    review = _make_review(customer_id=customer_id)
    review.collect_events()

    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = review

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = UpdateReviewHandler(review_repo, uow)
    command = UpdateReviewCommand(
        review_id=review.id,
        customer_id=customer_id,
        rating=2,
        comment="Changed my mind",
    )

    await handler.handle(command)
    review_repo.update.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_review_handler_not_found():
    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = None

    uow = AsyncMock()
    handler = UpdateReviewHandler(review_repo, uow)
    command = UpdateReviewCommand(
        review_id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        rating=3,
    )

    with pytest.raises(NotFoundException):
        await handler.handle(command)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_review_handler_wrong_customer():
    review = _make_review()

    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = review

    uow = AsyncMock()
    handler = UpdateReviewHandler(review_repo, uow)
    command = UpdateReviewCommand(
        review_id=review.id,
        customer_id=uuid.uuid4(),
        rating=1,
    )

    with pytest.raises(ValidationException, match="your own reviews"):
        await handler.handle(command)


# --- Application: ReplyToReviewHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reply_to_review_handler_success():
    review = _make_review()
    review.collect_events()

    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = review

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = ReplyToReviewHandler(review_repo, uow)
    command = ReplyToReviewCommand(review_id=review.id, reply="Thanks!")

    await handler.handle(command)
    assert review.reply == "Thanks!"
    review_repo.update.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_reply_to_review_handler_not_found():
    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = None

    uow = AsyncMock()
    handler = ReplyToReviewHandler(review_repo, uow)
    command = ReplyToReviewCommand(review_id=uuid.uuid4(), reply="Thanks!")

    with pytest.raises(NotFoundException):
        await handler.handle(command)


# --- Application: FlagReviewHandler ---


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flag_review_handler_success():
    review = _make_review()
    review.collect_events()

    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = review

    uow = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    handler = FlagReviewHandler(review_repo, uow)
    command = FlagReviewCommand(review_id=review.id, reason="Spam")

    await handler.handle(command)
    assert review.is_flagged is True
    review_repo.update.assert_called_once()
    uow.commit.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_flag_review_handler_not_found():
    review_repo = AsyncMock()
    review_repo.get_by_id.return_value = None

    uow = AsyncMock()
    handler = FlagReviewHandler(review_repo, uow)
    command = FlagReviewCommand(review_id=uuid.uuid4(), reason="Spam")

    with pytest.raises(NotFoundException):
        await handler.handle(command)
