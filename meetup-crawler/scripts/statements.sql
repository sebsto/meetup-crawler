select id,urlname,name,members,city,country from meetup_group as MG where last_updated_at = (select max(last_updated_at) from meetup_group where MG.id = id);  

select id,urlname,name,members,city,country, to_timestamp(last_updated_at) from meetup_group as MG where last_updated_at = (select max(last_updated_at) from meetup_group where MG.id = id);  

select id,urlname,name,members,city,country from meetup_group as MG where id = 9011772;

select id,urlname,name,members,city,country, to_timestamp(last_updated_at) from meetup_group as MG where id = 9011772; 