import datetime
import json
import os

import pandas as pd
from dateutil.parser import parse
from dotenv import load_dotenv

from helpers import get_page

load_dotenv()


def get_only_certain_attr(list_to_filter, keys):
    tmp_list = []
    if list_to_filter:
        for value in list_to_filter:
            features = {}
            for key in keys:
                features[key] = value[key]
            tmp_list.append(features)
        return json.dumps(tmp_list)


def get_listing_info(listing_id):
    url = "https://www.airbnb.com/api/v2/pdp_listing_details/" + str(
        listing_id)

    params = {"_format": "for_rooms_show",
              "key":     os.getenv("AIRBNB_KEY")}

    response = get_page(url, params)

    # TODO check response is not none in getting info in loop on other page
    none_conditions = {
        response is None,
        response.status_code != 200
    }

    if True in none_conditions:
        return None

    results = response.json()["pdp_listing_detail"]

    additional_house_rules = results["additional_house_rules"]
    bathroom_label = results["bathroom_label"]
    bed_label = results["bed_label"]
    bedroom_label = results["bedroom_label"]
    guest_label = results["guest_label"]
    name = results["name"]
    person_capacity = results["person_capacity"]
    photos = results["photos"]
    photo_count = len(photos)
    default_photo = photos[0]["large"]
    number_of_professional_photos = sum(
        photo["is_professional"] for photo in photos)
    host_name = results["primary_host"]["host_name"]
    languages = json.dumps(results["primary_host"]["languages"])
    room_and_property_type = results["room_and_property_type"]
    room_type_category = results["room_type_category"]
    is_plus = bool(results["tier_id"])
    min_nights = results["min_nights"]
    location_title = results["location_title"]
    localized_check_in_time_window = results[
        "localized_check_in_time_window"]
    localized_check_out_time = results["localized_check_out_time"]
    lat = results["lat"]
    lng = results["lng"]
    neighborhood_id = results["neighborhood_id"]
    license_number = results["license"]
    requires_license = results["requires_license"]
    support_cleaner_living_wage = results["support_cleaner_living_wage"]
    host_other_property_review_count = results["review_details_interface"][
        "host_other_property_review_count"]
    listing_review_count = results["review_details_interface"][
        "review_count"]
    listing_review_score = results["review_details_interface"][
        "review_score"]
    visible_review_count = results["visible_review_count"]
    host_interaction = results["host_interaction"]
    host_quote = results["host_quote"]
    is_select_market = results["is_select_market"]
    nearby_airport_distance_descriptions = json.dumps(results[
                                                          "nearby_airport_distance_descriptions"])
    is_hotel = results["is_hotel"]
    is_representative_inventory = results["is_representative_inventory"]
    has_essentials_amenity = results["has_essentials_amenity"]
    localized_overall_rating = results["reviews_module"][
        "localized_overall_rating"]
    discount_phrase = results["availability_module"]["discount_phrase"]
    host_badges = results["primary_host"]["badges"]
    host_intro_tags = results["primary_host"]["host_intro_tags"]

    amenities = json.dumps(results["listing_amenities"])
    highlights = json.dumps(results["highlights"])
    expectations = json.dumps(results["listing_expectations"])
    additional_hosts = json.dumps(results["additional_hosts"])
    review_summaries = json.dumps(
        results["review_details_interface"]["review_summary"])
    appreciation_tags = json.dumps(
        results["reviews_module"]["appreciation_tags"])
    rooms = json.dumps(results["listing_rooms"])
    primary_host = json.dumps(results["primary_host"])
    sectioned_description = json.dumps(results["sectioned_description"])
    guest_controls = json.dumps(results['guest_controls'])

    listing = {
        "additional_house_rules":         additional_house_rules,
        "bathroom_label":                 bathroom_label,
        "bed_label":                      bed_label,
        "bedroom_label":                  bedroom_label,
        "guest_label":                    guest_label,
        "id":                             results["id"],
        "name":                           name,
        "person_capacity":                person_capacity,
        "photo_count":                    photo_count,
        "default_photo":                  default_photo,
        "number_of_professional_photos":  number_of_professional_photos,
        "host_name":                      host_name,
        "languages":                      languages,
        "room_and_property_type":         room_and_property_type,
        "room_type_category":             room_type_category,
        "is_plus":                        is_plus,
        "min_nights":                     min_nights,
        "location_title":                 location_title,
        "localized_check_in_time_window": localized_check_in_time_window,
        "localized_check_out_time":       localized_check_out_time,
        "lat":                            lat,
        "lng":                            lng,
        "neighborhood_id":                neighborhood_id,
        "license":                        license_number,
        "requires_license":               requires_license,
        "support_cleaner_living_wage":    support_cleaner_living_wage,
        "host_other_property_review_count":
                                          host_other_property_review_count,
        "host_badges":                    host_badges,
        "host_intro_tags":                host_intro_tags,
        "listing_review_count":           listing_review_count,
        "listing_review_score":           listing_review_score,
        "visible_review_count":           visible_review_count,
        "host_interaction":               host_interaction,
        "host_quote":                     host_quote,
        "is_select_market":               is_select_market,
        "nearby_airport_descriptions":    nearby_airport_distance_descriptions,
        "is_hotel":                       is_hotel,
        "is_representative_inventory":    is_representative_inventory,
        "has_essentials_amenity":         has_essentials_amenity,
        "localized_overall_rating":       localized_overall_rating,
        "discount_phrase":                discount_phrase,
        "amenities":                      amenities,
        "highlights":                     highlights,
        "expectations":                   expectations,
        "additional_hosts":               additional_hosts,
        "review_summaries":               review_summaries,
        "appreciation_tags":              appreciation_tags,
        "rooms":                          rooms,
        'primary_host':                   primary_host,
        "sectioned_description":          sectioned_description,
        "guest_controls":                 guest_controls
    }

    return listing


def get_booking_info(listing_id, check_in, check_out, max_guests, min_nights):
    cleaning_fees = set()
    cancelation_policies = []
    non_refundable_discount_amount = 0
    extra_guest_fee = 0
    extra_guest_fee_at = 0

    params = {"_format":            "for_web_with_date",
              "key":                os.getenv("AIRBNB_KEY"),
              "listing_id":         listing_id,
              "check_in":           check_in,
              "check_out":          check_out,
              "number_of_children": 0,
              "number_of_infants":  0, }

    url = "https://www.airbnb.com/api/v2/pdp_listing_booking_details"
    for number_of_adults in range(1, max_guests + 1):

        params["number_of_adults"] = number_of_adults

        response = get_page(url, params)

        break_conditions = {
            response is None,
            response.status_code != 200
        }

        if True in break_conditions:
            break

        results = response.json()["pdp_listing_booking_details"][0]

        for price_item in results["price"]["price_items"]:
            if price_item["type"] == "CLEANING_FEE":
                cleaning_fees.add(price_item["total"]["amount"])

        if number_of_adults == 1:

            policy_keys = ["localized_cancellation_policy_name",
                           "cancellation_policy_label",
                           "cancellation_policy_price_type",
                           "cancellation_policy_price_factor",
                           "cancellation_policy_id",
                           "book_it_module_tooltip",
                           "subtitle"]
            policy_milestone_keys = ["titles", "subtitles", "type"]
            for policy in results["cancellation_policies"]:
                features = {"milestones": {}}
                for milestone in policy["milestones"]:
                    for key in policy_milestone_keys:
                        features["milestones"][key] = milestone[key]
                for key in policy_keys:
                    features[key] = policy[key]
                    if (key == "cancellation_policy_price_factor") and \
                            policy[
                                key] \
                            != 0:
                        non_refundable_discount_amount = policy[key]
                cancelation_policies.append(features)

        if results["extra_guest_fee"]["amount"] != 0:
            extra_guest_fee = results["extra_guest_fee"][
                                  "amount"] / min_nights
            extra_guest_fee_at = number_of_adults - 1
            break

    data = [list(cleaning_fees), cancelation_policies,
            non_refundable_discount_amount, extra_guest_fee,
            extra_guest_fee_at, check_in, check_out]

    return data


def get_reviews_info(listing_id, number_of_reviews):
    url = "https://www.airbnb.com/api/v2/homes_pdp_reviews"
    params = {"key":        os.getenv("AIRBNB_KEY"),
              "listing_id": listing_id,
              "limit":      number_of_reviews + 2}

    response = get_page(url, params)

    none_conditions = {
        response is None,
        response.status_code != 200
    }

    if True in none_conditions:
        return None

    reviews = response.json()["reviews"]

    oldest = None
    newest = None
    for review in reviews:
        created_at = parse(review["created_at"])
        if oldest:
            oldest = min(created_at, oldest)
        else:
            oldest = created_at
        if newest:
            newest = max(created_at, newest)
        else:
            newest = created_at
    return newest, oldest


def get_calendar_info(listing_id):
    url = "https://www.airbnb.com/api/v2/homes_pdp_availability_calendar"
    check_in = None
    check_out = None
    min_nights = None
    current_year_full = datetime.datetime.now().strftime("%Y")
    current_month = datetime.datetime.now().strftime("%m")
    params = {"key":        os.getenv("AIRBNB_KEY"),
              "listing_id": listing_id,
              "year":       current_year_full,
              "month":      current_month,
              "count":      12}

    response = get_page(url, params)

    none_conditions = {
        response is None,
        response.status_code != 200
    }

    if True in none_conditions:
        return None

    results = response.json()
    data = {}

    for month in results["calendar_months"]:
        for day in month["days"]:
            price = None
            bookable = False
            available_for_checkin = False
            if "local_price_formatted" in day["price"]:
                price = day["price"]["local_price_formatted"]

            data[day["date"]] = {"available":  day["available"],
                                 "max_nights": day["max_nights"],
                                 "min_nights": day["min_nights"],
                                 "price":      price}

            if 'bookable' in day:
                bookable = day['bookable']
                data[day["date"]]['bookable'] = day['bookable']
            if 'available_for_checkin' in day:
                available_for_checkin = day['available_for_checkin']
                data[day['date']]['available_for_checkin'] = day[
                    'available_for_checkin']
            if bookable and available_for_checkin:
                check_in = day["date"]
                check_in_date = datetime.datetime.strptime(day["date"],
                                                           "%Y-%m-%d")
                min_nights = day['min_nights']
                delta = datetime.timedelta(days=min_nights)
                check_out = (check_in_date + delta).strftime("%Y-%m-%d")

    return json.dumps(data), check_in, check_out, min_nights


def get_all_listing_info(listing_id):
    listing = get_listing_info(listing_id)
    if listing is None:
        return None

    calendar, check_in, check_out, min_nights = get_calendar_info(listing_id)
    if calendar is None:
        return None

    if check_in is None or check_out is None:
        print(listing_id)
        return None

    listing["calendar_info"] = calendar

    booking_info = get_booking_info(listing_id, check_in, check_out,
                                    listing["person_capacity"], min_nights)

    if booking_info is None:
        return None

    listing["cleaning_fee"] = json.dumps(booking_info[0])
    listing["cancelation_policies"] = json.dumps(booking_info[1])
    listing["non_refundable_discount_rate"] = booking_info[2]
    listing["extra_guest_fee"] = booking_info[3]
    listing["extra_guess_fee_at_greater_than"] = booking_info[4]
    listing["check_in"] = booking_info[5]
    listing["check_out"] = booking_info[6]
    listing["date_gathered"] = datetime.date.today().strftime(
        "%Y-%m-%d")

    review_count = listing["visible_review_count"]
    review_info = get_reviews_info(listing_id, review_count)

    if review_info is None:
        return None

    newest_comment, oldest_comment = review_info
    listing["newest_reviews_date"] = newest_comment
    listing["oldest_reviews_date"] = oldest_comment

    df = pd.DataFrame({k: [v] for k, v in listing.items()})

    return df
