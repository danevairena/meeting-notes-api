-- add llm column used for multi-llm note generation
alter table public.notes
add column if not exists llm text not null default 'gemini';

-- remove old unique constraint on meeting_id
drop index if exists idx_notes_meeting;

-- ensure uniqueness per meeting and llm
create unique index if not exists ux_notes_meeting_llm
on public.notes(meeting_id, llm);