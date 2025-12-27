-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Table 1: positions (Catálogo de situaciones únicas)
create table if not exists positions (
    zobrist_hash bigint primary key, -- Hash de 64-bits
    fen text, -- Representación legible (opcional, útil para debug)
    base_eval float, -- Evaluación de Stockfish
    shannon_entropy float, -- Métrica de complejidad cognitiva
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Table 2: decisions (La "Personalidad" del GM)
create table if not exists decisions (
    id uuid default uuid_generate_v4() primary key,
    gm_name text not null,
    zobrist_hash bigint references positions(zobrist_hash),
    move_chosen text not null, -- SAN notation
    move_time float, -- Tiempo de reflexión en segundos
    age_at_game int,
    elo_diff int,
    time_control_type text,
    game_date date,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Indexes for performance
create index if not exists idx_decisions_gm_name on decisions(gm_name);
create index if not exists idx_decisions_zobrist on decisions(zobrist_hash);
