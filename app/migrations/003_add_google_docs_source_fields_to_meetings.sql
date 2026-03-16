alter table meetings
add column if not exists source_url text,
add column if not exists external_id text;

create unique index if not exists meetings_external_source_idx
on meetings (source, external_id)
where external_id is not null;