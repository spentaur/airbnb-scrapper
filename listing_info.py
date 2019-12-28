import datetime
from random import uniform
from time import sleep

import pandas as pd
import requests
from dateutil.parser import parse


def get_listing_info(listing_id, attempts=0):
    url = 'https://www.airbnb.com/api/v2/pdp_listing_details/' + str(
        listing_id)

    params = {'_format': 'for_rooms_show',
              'key':     'd306zoyjsyarp7ifhu67rjxn52tv0t20'}

    max_attempts = 10

    r = requests.get(url, params)

    # check the status code
    status = r.status_code
    if status == 200:
        results = r.json()['pdp_listing_detail']

        additional_house_rules = results['additional_house_rules']
        bathroom_label = results['bathroom_label']
        bed_label = results['bed_label']
        bedroom_label = results['bedroom_label']
        guest_label = results['guest_label']
        name = results['name']
        person_capacity = results['person_capacity']
        photo_count = len(results['photos'])
        host_name = results['primary_host']['host_name']
        languages = results['primary_host']['languages']
        room_and_property_type = results['room_and_property_type']
        room_type_category = results['room_type_category']
        tier_id = results['tier_id']
        calendar_last_updated_at = results['calendar_last_updated_at']
        min_nights = results['min_nights']
        has_we_work_location = results['has_we_work_location']
        is_business_travel_ready = results['is_business_travel_ready']
        localized_check_in_time_window = results[
            'localized_check_in_time_window']
        localized_check_out_time = results['localized_check_out_time']
        lat = results['lat']
        lng = results['lng']
        neighborhood_id = results['neighborhood_id']
        license_number = results['license']
        requires_license = results['requires_license']
        support_cleaner_living_wage = results['support_cleaner_living_wage']
        host_other_property_review_count = results['review_details_interface'][
            'host_other_property_review_count']
        listing_review_count = results['review_details_interface'][
            'review_count']
        listing_review_score = results['review_details_interface'][
            'review_score']
        visible_review_count = results['visible_review_count']
        host_interaction = results['host_interaction']
        host_quote = results['host_quote']
        is_select_market = results['is_select_market']
        nearby_airport_distance_descriptions = results[
            'nearby_airport_distance_descriptions']
        is_hotel = results['is_hotel']
        is_representative_inventory = results['is_representative_inventory']
        has_essentials_amenity = results['has_essentials_amenity']
        security_deposit_details = results['security_deposit_details']
        localized_overall_rating = results['reviews_module'][
            'localized_overall_rating']
        discount_phrase = results['availability_module']['discount_phrase']
        amenities_keys = ['id', 'is_business_ready_feature', 'is_present',
                          'is_safety_feature', 'name']
        amenities = get_only_certain_attr(results['listing_amenities'],
                                          amenities_keys)
        highlights_keys = ['type', 'message', 'headline']
        highlights = get_only_certain_attr(results['highlights'],
                                           highlights_keys)
        expectations_keys = ['type', 'title']
        expectations = get_only_certain_attr(results['listing_expectations'],
                                             expectations_keys)
        additional_hosts_keys = ['id', 'member_since', 'host_name',
                                 'profile_pic_path']
        additional_hosts = get_only_certain_attr(results['additional_hosts'],
                                                 additional_hosts_keys)
        review_summaries_keys = ['category', 'value', 'localized_rating',
                                 'percentage']
        review_summaries = get_only_certain_attr(
            results['review_details_interface']['review_summary'],
            review_summaries_keys)
        appreciation_tags_keys = ['localized_text', 'localized_count_string']
        appreciation_tags = get_only_certain_attr(results['reviews_module'][
                                                      'appreciation_tags'],
                                                  appreciation_tags_keys)

        listing = {'additional_house_rules':      additional_house_rules,
                   'bathroom_label':              bathroom_label,
                   'bed_label':                   bed_label,
                   'bedroom_label':               bedroom_label,
                   'guest_label':                 guest_label,
                   'id':                          results['id'],
                   'name':                        name,
                   'person_capacity':             person_capacity,
                   'photo_count':                 photo_count,
                   'host_name':                   host_name,
                   'languages':                   languages,
                   'room_and_property_type':      room_and_property_type,
                   'room_type_category':          room_type_category,
                   'tier_id':                     tier_id,
                   'calendar_last_updated_at':
                                                  calendar_last_updated_at,
                   'min_nights':                  min_nights,
                   'has_we_work_location':        has_we_work_location,
                   'is_business_travel_ready':
                                                  is_business_travel_ready,
                   'localized_check_in_time_window':
                                                  localized_check_in_time_window,
                   'localized_check_out_time':
                                                  localized_check_out_time,
                   'lat':                         lat,
                   'lng':                         lng,
                   'neighborhood_id':             neighborhood_id,
                   'license':                     license_number,
                   'requires_license':            requires_license,
                   'support_cleaner_living_wage':
                                                  support_cleaner_living_wage,
                   'host_other_property_review_count':
                                                  host_other_property_review_count,
                   'listing_review_count':        listing_review_count,
                   'listing_review_score':        listing_review_score,
                   'visible_review_count':        visible_review_count,
                   'host_interaction':            host_interaction,
                   'host_quote':                  host_quote,
                   'is_select_market':            is_select_market,
                   'nearby_airport_distance_descriptions':
                                                  nearby_airport_distance_descriptions,
                   'is_hotel':                    is_hotel,
                   'is_representative_inventory': is_representative_inventory,
                   'has_essentials_amenity':      has_essentials_amenity,
                   'security_deposit_details':    security_deposit_details,
                   'localized_overall_rating':    localized_overall_rating,
                   'discount_phrase':             discount_phrase,
                   'amenities':                   amenities,
                   'highlights':                  highlights,
                   'expectations':                expectations,
                   'additional_hosts':            additional_hosts,
                   'review_summaries':            review_summaries,
                   'appreciation_tags':           appreciation_tags
                   }

        rooms = {}
        for room in results['listing_rooms']:
            room_number = room['room_number']
            beds = []
            beds_keys = ['quantity', 'type']
            for bed in room['beds']:
                features = {}
                for key in beds_keys:
                    features[key] = bed[key]
                beds.append(features)
            rooms[room_number] = beds
        listing['rooms'] = rooms

        host_keys = ['id', 'identity_verified', 'is_superhost',
                     'member_since', 'response_rate_without_na',
                     'response_time_without_na', 'has_inclusion_badge',
                     'profile_pic_path_large']
        for key in host_keys:
            listing[f"host_{key}"] = results['primary_host'][key]

        sectioned_description_keys = ['access', 'description', 'house_rules',
                                      'interaction', 'neighborhood_overview',
                                      'notes', 'space', 'summary', 'transit']

        for key in sectioned_description_keys:
            listing[key] = results['sectioned_description'][key]

        guest_controls_keys = ['allows_children', 'allows_infants',
                               'allows_infants', 'allows_smoking',
                               'allows_events', 'host_check_in_time_message',
                               'allows_non_china_users']

        for key in guest_controls_keys:
            listing[key] = results['guest_controls'][key]

        if results['education_modules']['plus_education_module_v1'] or \
                results['education_modules']['plus_education_module_v2']:
            listing['is_plus'] = True
        else:
            listing['is_plus'] = False

        return listing
    else:
        # if the status code is not 200, something went wrong and
        # let's just sleep and the request will be repeated. this
        # repeats the while loop so nothing get's changed it's just
        # the same request over again right? should verify that

        # increment attempts

        if attempts <= max_attempts:
            attempts += 1
            print("listing info")
            print("status code", status)
            sleep_for = uniform(1, 10)
            print('sleeping for:', sleep_for)
            sleep(sleep_for)
            get_listing_info(listing_id, attempts)
        else:
            return 420


def get_only_certain_attr(list_to_filter, keys):
    tmp_list = []
    if list_to_filter:
        for value in list_to_filter:
            features = {}
            for key in keys:
                features[key] = value[key]
            tmp_list.append(features)
        return tmp_list


def get_booking_info(listing_id, min_nights, max_guests):
    today = datetime.date.today()
    delta = datetime.timedelta(days=14)
    delta_min_nights = datetime.timedelta(days=min_nights)
    check_in = (today + delta).strftime("%Y-%m-%d")
    check_out = ((today + delta) + delta_min_nights).strftime("%Y-%m-%d")

    cleaning_fee = 0
    cancelation_policies = []
    non_refundable_discount_amount = 0
    extra_guest_fee = 0
    extra_guest_fee_at = 0

    counter = 0
    max_attempts = 10
    attempts = 0
    broken = False
    number_of_adults = 1

    url = 'https://www.airbnb.com/api/v2/pdp_listing_booking_details'
    while number_of_adults <= max_guests:
        params = {'_format':            'for_web_with_date',
                  'key':                'd306zoyjsyarp7ifhu67rjxn52tv0t20',
                  'listing_id':         listing_id,
                  'check_in':           check_in,
                  'check_out':          check_out,
                  'number_of_children': 0,
                  'number_of_infants':  0,
                  'number_of_adults':   number_of_adults}
        r = requests.get(url, params)
        # check the status code
        status = r.status_code
        if status == 200:
            attempts = 0
            results = r.json()['pdp_listing_booking_details'][0]

            if counter == 0:
                for price_item in results['price']['price_items']:
                    if price_item['type'] == "CLEANING_FEE":
                        cleaning_fee = price_item['total']['amount']

                policy_keys = ['localized_cancellation_policy_name',
                               'cancellation_policy_label',
                               'cancellation_policy_price_type',
                               'cancellation_policy_price_factor',
                               'cancellation_policy_id',
                               'book_it_module_tooltip',
                               'subtitle']
                policy_milestone_keys = ['titles', 'subtitles', 'type']
                for policy in results['cancellation_policies']:
                    features = {'milestones': {}}
                    for milestone in policy['milestones']:
                        for key in policy_milestone_keys:
                            features['milestones'][key] = milestone[key]
                    for key in policy_keys:
                        features[key] = policy[key]
                        if (key == 'cancellation_policy_price_factor') and \
                                policy[
                                    key] \
                                != 0:
                            non_refundable_discount_amount = policy[key]
                    cancelation_policies.append(features)

            if results['extra_guest_fee']['amount'] != 0:
                extra_guest_fee = results['extra_guest_fee'][
                                      'amount'] / min_nights
                extra_guest_fee_at = number_of_adults - 1
                break

            counter += 1
            number_of_adults += 1

            # sleep_for = uniform(4, 20)
            # sleep(sleep_for)
        else:
            # if the status code is not 200, something went wrong and
            # let's just sleep and the request will be repeated. this
            # repeats the while loop so nothing get's changed it's just
            # the same request over again right? should verify that

            # increment attempts
            attempts += 1
            if attempts > max_attempts:
                broken = True
                break
            print("booking info")
            print("status code", status)
            sleep_for = uniform(1, 10)
            print('sleeping for:', sleep_for)
            sleep(sleep_for)

    if not broken:
        data = [cleaning_fee, cancelation_policies,
                non_refundable_discount_amount, extra_guest_fee,
                extra_guest_fee_at, check_in, check_out]

        return data
    else:
        return 420


def get_reviews_info(listing_id, number_of_reviews):
    url = 'https://www.airbnb.com/api/v2/homes_pdp_reviews'
    # TODO add key to a variable
    params = {'key':        'd306zoyjsyarp7ifhu67rjxn52tv0t20',
              'listing_id': listing_id,
              'limit':      number_of_reviews}

    max_attempts = 10
    attempts = 0

    while attempts < max_attempts:
        r = requests.get(url=url, params=params)
        if r.status_code == 200:
            reviews = r.json()['reviews']

            assert (len(reviews) == number_of_reviews)

            oldest = None
            newest = None
            for review in reviews:
                created_at = parse(review['created_at'])
                if oldest:
                    oldest = min(created_at, oldest)
                else:
                    oldest = created_at
                if newest:
                    newest = max(created_at, newest)
                else:
                    newest = created_at

            # TODO i dont think i need this since i'm returning?
            attempts = max_attempts
            return newest, oldest
        else:
            attempts += 1
            print("comments")
            print("status code", r.status_code)
            sleep_for = uniform(1, 10)
            print('sleeping for:', sleep_for)
            sleep(sleep_for)

    return 420


def get_all_listing_info(listing_id):
    listing = get_listing_info(listing_id)
    # TODO i think it actually reurns none so i need to redo retries,
    #  just fail if anything else but 200
    if listing != 420:
        booking_info = get_booking_info(listing_id, listing['min_nights'],
                                        listing['person_capacity'])

        if booking_info != 420:
            listing['cleaning_fee'] = booking_info[0]
            listing['cancelation_policies'] = booking_info[1]
            listing['non_refundable_discount_rate'] = booking_info[2]
            listing['extra_guest_fee'] = booking_info[3]
            listing['extra_guess_fee_at_greater_than'] = booking_info[4]
            listing['check_in'] = booking_info[5]
            listing['check_out'] = booking_info[6]
            listing['date_gathered'] = datetime.date.today().strftime(
                "%Y-%m-%d")

            comment_count = listing['visible_review_count']
            comment_info = get_reviews_info(listing_id, comment_count)
            if comment_info != 420:
                newest_comment, oldest_comment = comment_info
                listing['newest_reviews_date'] = newest_comment
                listing['oldest_reviews_date'] = oldest_comment

            df = pd.DataFrame({k: [v] for k, v in listing.items()})

            return df
