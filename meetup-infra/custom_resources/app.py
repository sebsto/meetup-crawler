

create_meetup_group_sql = "CREATE TABLE IF NOT EXISTS meetup_group (id BIGINT, name VARCHAR, status VARCHAR, link VARCHAR, urlname VARCHAR, description VARCHAR, created BIGINT, city VARCHAR, untranslated_city VARCHAR, country VARCHAR, localized_country_name VARCHAR, localized_location VARCHAR, region2 VARCHAR, state VARCHAR, join_mode VARCHAR, visibility VARCHAR, lat NUMERIC, lon NUMERIC, members BIGINT, member_pay_fee BOOLEAN, timezone VARCHAR, last_updated_at BIGINT, raw_json JSON NOT NULL);"

create_meetup_event_sql = "CREATE TABLE IF NOT EXISTS meetup_event ( \
    id VARCHAR PRIMARY KEY, \
    utc_offset BIGINT, rsvp_limit BIGINT, headcount BIGINT, visibility VARCHAR, \
    waitlist_count BIGINT, created BIGINT, maybe_rsvp_count BIGINT, description VARCHAR, why VARCHAR, \
    how_to_find_us VARCHAR, event_url VARCHAR, yes_rsvp_count BIGINT, name VARCHAR, \
    time BIGINT, duration BIGINT, updated BIGINT, photo_url VARCHAR, \
    \
    -- flattened structures \
    \
    fee_amount BIGINT, fee_accepts VARCHAR, fee_description VARCHAR, fee_currency VARCHAR, fee_label VARCHAR, fee_required VARCHAR, \
    \
    venue_country VARCHAR, venue_localized_country_name VARCHAR, venue_city VARCHAR, venue_state VARCHAR, venue_address_1 VARCHAR, \
    venue_address_2 VARCHAR, venue_name VARCHAR, venue_lon NUMERIC, venue_id BIGINT, venue_lat NUMERIC, venue_repinned BOOLEAN, \
    venue_phone VARCHAR, venue_zip VARCHAR, \
    \
    rating_count BIGINT, rating_average BIGINT, \
    \
    group_join_mode VARCHAR, group_created BIGINT, group_name VARCHAR, group_group_lon NUMERIC, group_id BIGINT, \
    group_urlname VARCHAR, group_group_lat NUMERIC, group_who VARCHAR, \
    \
    last_updated_at BIGINT, raw_json JSON NOT NULL);"

create_meetup_group_view_sql = "CREATE OR REPLACE VIEW meetup_group_latest AS \
    SELECT *  \
    FROM meetup_group AS MG \
    WHERE last_updated_at = (SELECT max(last_updated_at) FROM meetup_group WHERE MG.id = id);"

def on_event(event, context):
  print(event)
  request_type = event['RequestType']
  if request_type == 'Create': return on_create(event)
  if request_type == 'Update': return on_update(event)
  if request_type == 'Delete': return on_delete(event)
  raise Exception("Invalid request type: %s" % request_type)

def on_create(event):
  props = event["ResourceProperties"]
  print("create new resource with props %s" % props)

  # add your create code here...
  physical_id = "123"

  return { 'PhysicalResourceId': physical_id }

def on_update(event):
  physical_id = event["PhysicalResourceId"]
  props = event["ResourceProperties"]
  print("update resource %s with props %s" % (physical_id, props))
  # ...

def on_delete(event):
  physical_id = event["PhysicalResourceId"]
  print("delete resource %s" % physical_id)
  # ...