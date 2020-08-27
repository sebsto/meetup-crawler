drop table meetup_group;
CREATE TABLE IF NOT EXISTS meetup_group (id BIGINT, name VARCHAR, status VARCHAR, link VARCHAR, urlname VARCHAR, description VARCHAR, created BIGINT, city VARCHAR, untranslated_city VARCHAR, country VARCHAR, localized_country_name VARCHAR, localized_location VARCHAR, region2 VARCHAR, state VARCHAR, join_mode VARCHAR, visibility VARCHAR, lat NUMERIC, lon NUMERIC, members BIGINT, member_pay_fee BOOLEAN, timezone VARCHAR, last_updated_at BIGINT, raw_json JSON NOT NULL);

drop table meetup_event;
CREATE TABLE IF NOT EXISTS meetup_event (
    utc_offset BIGINT, rsvp_limit BIGINT, headcount BIGINT, visibility VARCHAR,
    waitlist_count BIGINT, created BIGINT, maybe_rsvp_count BIGINT, description VARCHAR,
    how_to_find_us VARCHAR, event_url VARCHAR, yes_rsvp_count BIGINT, name VARCHAR, id VARCHAR,
    time BIGINT, duration BIGINT, updated BIGINT, photo_url VARCHAR,
    
    -- flattened structures 
    
    fee_amount BIGINT, fee_accepts VARCHAR, fee_description VARCHAR, fee_currency VARCHAR, fee_label VARCHAR, fee_required VARCHAR,
    
    venue_country VARCHAR, venue_localized_country_name VARCHAR, venue_city VARCHAR, venue_state VARCHAR, venue_address_1 VARCHAR,
    venue_address_2 VARCHAR, venue_name VARCHAR, venue_lon NUMERIC, venue_id BIGINT, venue_lat NUMERIC, venue_repinned BOOLEAN,
    
    rating_count BIGINT, rating_average BIGINT,
    
    group_join_mode VARCHAR, group_created BIGINT, group_name VARCHAR, group_group_lon NUMERIC, group_id BIGINT,
    group_urlname VARCHAR, group_group_lat NUMERIC, group_who VARCHAR,
    
    last_updated_at BIGINT, raw_json JSON NOT NULL);


select id,urlname,name,members,city,country from meetup_group as MG where last_updated_at = (select max(last_updated_at) from meetup_group where MG.id = id);  

select id,urlname,name,members,city,country, to_timestamp(last_updated_at) from meetup_group as MG where last_updated_at = (select max(last_updated_at) from meetup_group where MG.id = id);  

select id,urlname,name,members,city,country from meetup_group as MG where id = 9011772;

select id,urlname,name,members,city,country, to_timestamp(last_updated_at) from meetup_group as MG where id = 9011772; 