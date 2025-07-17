from datetime import datetime, timedelta

from core.logging_config import get_logger
from models.coordinates_model import Coordinates
from models.event_model import EventDetails
from models.user_profile_model import UserProfile
from utils.address_utils import calculate_distance
from utils.age_utils import get_age_from_birth_date
from utils.date_utils import time_to_string

logger = get_logger(__name__)


def normalize_datetime(dt1: datetime, dt2: datetime) -> tuple[datetime, datetime]:
    """Take timezone from the aware datetime and apply it to the naive one."""
    if dt1.tzinfo is None and dt2.tzinfo is not None:
        return dt1.replace(tzinfo=dt2.tzinfo), dt2
    elif dt1.tzinfo is not None and dt2.tzinfo is None:
        return dt1, dt2.replace(tzinfo=dt1.tzinfo)
    return dt1, dt2


class EventDisqualifier:
    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile

    def check_compatibility(self, event_details: EventDetails) -> bool:
        # Check all quick conditions first
        checks = [
            self._is_event_sold_out,
            self._is_event_within_acceptable_distance,
            self._is_event_within_acceptable_price_range,
            self._is_event_within_time_commitment,
            self._is_event_within_acceptable_age_range,
            self._is_event_suitable_for_gender,
            self._is_event_suitable_for_sexual_orientation,
            self._is_event_suitable_for_relationship_status,
            self._is_event_suitable_for_event_format,
            self._is_event_within_acceptable_times,
            self._is_not_past_event,
            self._is_event_page_non_empty,
        ]

        return all(check(event_details) for check in checks)

    def _is_event_sold_out(self, event_details: EventDetails) -> bool:
        if event_details["is_sold_out"]:
            logger.info("Event is sold out")
            return False

        return True

    def _is_event_within_acceptable_distance(self, event_details: EventDetails) -> bool:
        # If user has no location or distance threshold, distance is not a factor
        if not self.user_profile.location or not self.user_profile.distance_threshold:
            return True

        event_location = event_details.get("location_of_event")
        if not event_location:
            # If event has no location, we can't calculate distance
            return True

        if not event_location.latitude or not event_location.longitude:
            # If event has no coordinates, we can't calculate distance
            return True

        latitude = event_location.latitude
        longitude = event_location.longitude
        assert latitude is not None and longitude is not None

        event_coordinates: Coordinates = Coordinates(
            latitude=latitude, longitude=longitude
        )
        distance = calculate_distance(
            loc1=self.user_profile.location,
            loc2=event_coordinates,
            distance_unit=self.user_profile.distance_threshold.unit,
        )

        # Check if the event is within the user's acceptable distance
        max_distance = self.user_profile.distance_threshold.distance_threshold
        within_threshold = distance <= max_distance

        if not within_threshold:
            logger.info("Event is too far")
            return False

        return within_threshold

    def _is_event_within_acceptable_price_range(
        self, event_details: EventDetails
    ) -> bool:
        if event_details["price_of_event"] and not self.user_profile.willingness_to_pay:
            logger.info("Event is paid and the user doesn't want to pay")
            return False

        if event_details["price_of_event"] and self.user_profile.willingness_to_pay:
            if event_details["price_of_event"] > self.user_profile.budget:
                logger.info(
                    "Event is paid and the price is higher than the user's budget"
                )
                return False

        return True

    def _is_event_within_time_commitment(self, event_details: EventDetails) -> bool:
        if (
            event_details["start_time"]
            and event_details["end_time"]
            and self.user_profile.time_commitment_in_minutes
        ):
            start_time_str = time_to_string(event_details["start_time"])
            end_time_str = time_to_string(event_details["end_time"])

            if start_time_str and end_time_str:
                start_time = datetime.strptime(start_time_str, "%H:%M")
                end_time = datetime.strptime(end_time_str, "%H:%M")

                time_difference = end_time - start_time
                if (
                    time_difference.total_seconds()
                    > self.user_profile.time_commitment_in_minutes * 60
                ):
                    logger.info(
                        "Event is longer than the user's acceptable time commitment"
                    )
                    return False

        return True

    def _is_event_within_acceptable_age_range(
        self, event_details: EventDetails
    ) -> bool:
        AGE_MARGIN = 2  # 2-year margin of tolerance
        user_age = get_age_from_birth_date(self.user_profile.birth_date)

        if event_details["age_range"]:
            if event_details["age_range"]["min_age"]:
                if event_details["age_range"]["min_age"] > user_age + AGE_MARGIN:
                    logger.info("Event is outside the user's acceptable age range")
                    return False
            if event_details["age_range"]["max_age"]:
                if event_details["age_range"]["max_age"] < user_age - AGE_MARGIN:
                    logger.info("Event is outside the user's acceptable age range")
                    return False

        return True

    def _is_event_suitable_for_gender(self, event_details: EventDetails) -> bool:
        if event_details["gender_bias"] and self.user_profile.gender:
            if self.user_profile.gender not in event_details["gender_bias"]:
                logger.info("Event is not suitable for the user's gender")
                return False

        return True

    def _is_event_suitable_for_sexual_orientation(
        self, event_details: EventDetails
    ) -> bool:
        if (
            event_details["sexual_orientation_bias"]
            and self.user_profile.sexual_orientation
        ):
            if (
                self.user_profile.sexual_orientation
                not in event_details["sexual_orientation_bias"]
            ):
                logger.info("Event is not suitable for the user's sexual orientation")
                return False

        return True

    def _is_event_suitable_for_relationship_status(
        self, event_details: EventDetails
    ) -> bool:
        if (
            event_details["relationship_status_bias"]
            and self.user_profile.relationship_status
        ):
            if (
                self.user_profile.relationship_status
                not in event_details["relationship_status_bias"]
            ):
                logger.info("Event is not suitable for the user's relationship status")
                return False

        return True

    def _is_event_suitable_for_event_format(self, event_details: EventDetails) -> bool:
        if not event_details["event_format"]:
            return True

        if (
            not self.user_profile.willingness_for_online
            and "online" in event_details["event_format"]
            and "offline" not in event_details["event_format"]
        ):
            logger.info(
                "Event is online-only and the user is unwilling to attend online events"
            )
            return False

        return True

    def _is_event_within_acceptable_times(self, event_details: EventDetails) -> bool:
        if not self.user_profile.acceptable_times:
            return True

        date_of_event = event_details.get("date_of_event")
        if not date_of_event:
            return True

        # We've checked that date_of_event is not None above
        is_weekday = datetime.strptime(date_of_event, "%d-%m-%Y").weekday() < 5

        if is_weekday:
            weekday_start_time = self.user_profile.acceptable_times.weekdays.start
            if event_details["start_time"] and weekday_start_time:
                start_time_str = time_to_string(event_details["start_time"])

                if start_time_str:
                    start_time = datetime.strptime(start_time_str, "%H:%M")
                    start_time_user = datetime.strptime(weekday_start_time, "%H:%M")
                    # Add 30 minutes padding to start time
                    start_time_user = start_time_user - timedelta(minutes=30)

                    start_time, start_time_user = normalize_datetime(
                        start_time, start_time_user
                    )

                    if start_time < start_time_user:
                        logger.info("Event is before the user's acceptable times")
                        return False

            weekday_end_time = self.user_profile.acceptable_times.weekdays.end
            if event_details["end_time"] and weekday_end_time:
                end_time_str = time_to_string(event_details["end_time"])

                if end_time_str:
                    end_time = datetime.strptime(end_time_str, "%H:%M")
                    end_time_user = datetime.strptime(weekday_end_time, "%H:%M")
                    # Add 30 minutes padding to end time
                    end_time_user = end_time_user + timedelta(minutes=30)

                    end_time, end_time_user = normalize_datetime(
                        end_time, end_time_user
                    )

                    if end_time > end_time_user:
                        logger.info("Event is after the user's acceptable times")
                        return False

        else:
            weekend_start_time = self.user_profile.acceptable_times.weekends.start
            if event_details["start_time"] and weekend_start_time:
                start_time_str = time_to_string(event_details["start_time"])

                if start_time_str:
                    start_time = datetime.strptime(start_time_str, "%H:%M")
                    start_time_user = datetime.strptime(weekend_start_time, "%H:%M")
                    # Add 30 minutes padding to start time
                    start_time_user = start_time_user - timedelta(minutes=30)

                    start_time, start_time_user = normalize_datetime(
                        start_time, start_time_user
                    )

                    if start_time < start_time_user:
                        logger.info("Event is before the user's acceptable times")
                        return False

            weekend_end_time = self.user_profile.acceptable_times.weekends.end
            if event_details["end_time"] and weekend_end_time:
                end_time_str = time_to_string(event_details["end_time"])

                if end_time_str:
                    end_time = datetime.strptime(end_time_str, "%H:%M")
                    end_time_user = datetime.strptime(weekend_end_time, "%H:%M")
                    # Add 30 minutes padding to end time
                    end_time_user = end_time_user + timedelta(minutes=30)

                    end_time, end_time_user = normalize_datetime(
                        end_time, end_time_user
                    )

                    if end_time > end_time_user:
                        logger.info("Event is after the user's acceptable times")
                        return False

        return True

    def _is_not_past_event(self, event_details: EventDetails) -> bool:
        event_date_str = event_details["date_of_event"]
        if not event_date_str:
            return True

        event_date = datetime.strptime(event_date_str, "%d-%m-%Y")
        if event_date < datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            logger.info("Event is in the past")
            return False

        return True

    def _is_event_page_non_empty(self, event_details: EventDetails) -> bool:
        if (
            not event_details["title"]
            and not event_details["date_of_event"]
            and not event_details["start_time"]
            and not event_details["end_time"]
            and not event_details["location_of_event"]
            and not event_details["event_format"]
        ):
            logger.info("Event page is empty")
            return False

        return True
