from enum import StrEnum


class LoyaltyTier(StrEnum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"


class BookingType(StrEnum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    CRUISE = "cruise"
    CAR_RENTAL = "car_rental"
    PACKAGE = "package"
    OTHER = "other"
