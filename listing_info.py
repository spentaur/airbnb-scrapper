import requests


def get_listing_info(listing_id):
    url = 'https://www.airbnb.com/api/v2/pdp_listing_details/' + listing_id

    params = {'_format': 'for_rooms_show',
              'key':     'd306zoyjsyarp7ifhu67rjxn52tv0t20'}

    # TODO retries
    r = requests.get(url, params)
    results = r.json()['pdp_listing_detail']

    additional_house_rules = results['additional_house_rules']
    bathroom_label = results['bathroom_label']
    bed_label = results['bed_label']
    bedroom_label = results['bedroom_label']
    guest_label = results['guest_label']
    name = results['name']
    person_capacity = results['person_capacity']
    photo_count = len(results['photos'])
    host_name = results['host_name']
    has_languages = len(results['primary_host']['languages']) > 0
    room_and_property_type = results['room_and_property_type']
    room_type_category = results['room_type_category']
    tier_id = results['tier_id']
    calendar_last_updated_at = results['calendar_last_updated_at']
    min_nights = results['min_nights']
    has_we_work_location = results['has_we_work_location']
    is_business_travel_ready = results['is_business_travel_ready']
    localized_check_in_time_window = results['localized_check_in_time_window']
    localized_check_out_time = results['localized_check_out_time']
    lat = results['lat']
    lng = results['lng']
    neighborhood_id = results['neighborhood_id']
    license_number = results['license']
    requires_license = results['requires_license']
    support_cleaner_living_wage = results['support_cleaner_living_wage']
    host_other_property_review_count = results['review_details_interface'][
        'host_other_property_review_count']
    listing_review_count = results['review_details_interface']['review_count']
    listing_review_score = results['review_details_interface']['review_score']
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
    highlights = get_only_certain_attr(results['highlights'], highlights_keys)
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
                                                  'app  reciation_tags'],
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
               'has_languages':               has_languages,
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

    # TODO check rooms
    rooms = {}
    for room in listing['listing_rooms']:
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

    # TODO badges, just add this to dict
    host_keys = ['id', 'identity_verified', 'is_superhost',
                 'member_since', 'response_rate_without_na',
                 'response_time_without_na', 'has_inclusion_badge',
                 'profile_pic_path_large']
    for key in host_keys:
        listing[f"host_{key}"] = results[key]

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

    # TODO is_plus


def get_only_certain_attr(list_to_filter, keys):
    tmp_list = []
    for value in list_to_filter:
        features = {}
        for key in keys:
            features[key] = value[key]
        tmp_list.append(features)
    return tmp_list
