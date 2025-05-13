-- messages table
create table if not exists messages (
  id uuid default uuid_generate_v4() primary key,
  id_user int not null,
  timestamp timestamptz not null,
  source text check (source in ('livechat','telegram')),
  message text,
  category text,
  created_at timestamptz default now()
);