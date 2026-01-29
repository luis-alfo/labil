# Plan de Deployment - Labil

## Stack confirmado
- **Repo**: GitHub
- **Frontend**: Vercel
- **Backend/DB**: Supabase (auth + postgres)
- **AI**: OpenAI/Anthropic (nuestra key)
- **Dominio**: labil.app

## Decisiones tomadas ✓

### 1. Autenticación
- [x] Login obligatorio
- [x] Providers: Google, Email/password, Magic link

### 2. Persistencia
- [x] Diagramas en Supabase
- [x] Historial de versiones en DB

### 3. API Keys & Límites
- [x] Nuestra API key (no BYOK)
- [x] Sistema de créditos con metáfora química (termolabilidad)
- [x] Opción "barra libre" para algunos usuarios

### 4. Dominio
- [x] labil.app

### 5. Monetización
- [x] Free tier con límites (futuro)
- [x] No monetización inicial

---

## Pasos de implementación

### Fase 1: Repo + Deploy básico
1. Crear repo en GitHub
2. Conectar a Vercel
3. Configurar env vars (OPENAI_API_KEY)
4. Deploy inicial

### Fase 2: Supabase
1. Crear proyecto Supabase
2. Diseñar schema (users, projects, diagrams)
3. Configurar auth
4. Migrar de localStorage a Supabase

### Fase 3: Features pro
1. Colaboración real-time
2. Compartir diagramas (links públicos)
3. Export a PNG/SVG/PDF

---

## Sistema de créditos: "Energía"

Metáfora química relacionada con termolabilidad:

| Concepto | Nombre propuesto | Descripción |
|----------|------------------|-------------|
| Créditos | **Julios (J)** | Unidad de energía, simple y reconocible |
| Alternativa | **kcal** | Kilocalorías, más "químico" |
| Alternativa | **ATP** | Adenosín trifosfato, la "moneda energética" celular |
| Alternativa | **eV** | Electronvoltios, más técnico |

**Propuesta**: Usar **"Energía"** como concepto y **"J"** (Julios) como unidad.
- "Te quedan 500J de energía"
- "Esta operación consume ~50J"
- "Barra libre" = energía infinita (∞J)

### Conversión tokens → Julios
```
1 Julio ≈ 1000 tokens (input + output)
Usuario free: 100J/mes (~100k tokens)
Usuario pro: 1000J/mes
Barra libre: ∞J
```

---

## Schema Supabase

```sql
-- Users (extendido de Supabase Auth)
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  name text,
  avatar_url text,
  -- Sistema de energía
  energy_balance integer default 100, -- Julios disponibles
  energy_unlimited boolean default false, -- Barra libre
  tier text default 'free', -- free | pro | unlimited
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Projects
create table projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete cascade,
  name text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Diagrams (versiones)
create table diagrams (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id) on delete cascade,
  nodes jsonb not null,
  edges jsonb not null,
  title text,
  prompt text, -- El prompt que generó este diagrama
  created_at timestamptz default now()
);

-- Energy usage log (para analytics)
create table energy_log (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references profiles(id) on delete cascade,
  project_id uuid references projects(id) on delete set null,
  tokens_used integer not null,
  julios_consumed numeric(10,2) not null,
  model text, -- gpt-4o, claude-3, etc.
  created_at timestamptz default now()
);

-- RLS policies
alter table profiles enable row level security;
alter table projects enable row level security;
alter table diagrams enable row level security;
alter table energy_log enable row level security;

create policy "Users can read own profile"
  on profiles for select using (auth.uid() = id);

create policy "Users can update own profile"
  on profiles for update using (auth.uid() = id);

create policy "Users can CRUD own projects"
  on projects for all using (auth.uid() = user_id);

create policy "Users can CRUD diagrams of own projects"
  on diagrams for all using (
    project_id in (select id from projects where user_id = auth.uid())
  );

create policy "Users can read own energy log"
  on energy_log for select using (auth.uid() = user_id);

-- Trigger para crear profile al registrarse
create or replace function handle_new_user()
returns trigger as $$
begin
  insert into profiles (id, email, name, avatar_url)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.raw_user_meta_data->>'avatar_url'
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();
```

---

## Env vars

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# AI
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# App
NEXT_PUBLIC_APP_URL=https://labil.app
```

---

## Fases de implementación

### Fase 1: Repo + Deploy básico (1-2h)
- [ ] Crear repo en GitHub
- [ ] Limpiar código (quitar .env.local, etc.)
- [ ] Añadir .gitignore robusto
- [ ] Conectar a Vercel
- [ ] Deploy inicial (sin auth, sin DB)

### Fase 2: Supabase Auth (2-3h)
- [ ] Crear proyecto Supabase
- [ ] Configurar providers:
  - [ ] Google OAuth
  - [ ] Email/password
  - [ ] Magic link (passwordless)
- [ ] Crear schema inicial
- [ ] Implementar login/logout en frontend
- [ ] Proteger rutas

### Fase 3: Persistencia (3-4h)
- [ ] Migrar de localStorage a Supabase
- [ ] CRUD de projects
- [ ] CRUD de diagrams (versiones)
- [ ] Sincronización optimista

### Fase 4: Sistema de energía (2-3h)
- [ ] Tracking de tokens usados
- [ ] UI de energía restante
- [ ] Lógica de límites
- [ ] Flag de barra libre

### Fase 5: Polish (2h)
- [ ] Onboarding flow
- [ ] Empty states
- [ ] Error handling
- [ ] Loading states

---

## ✅ Todas las decisiones tomadas

| Decisión | Valor |
|----------|-------|
| Auth obligatorio | Sí |
| Providers | Google, Email/pw, Magic link |
| Persistencia | Supabase |
| API key | Nuestra (con límites) |
| Sistema créditos | Julios (J) |
| Dominio | labil.app |
| Monetización | Futura |

---

## Próximo paso: Fase 1

¿Tienes ya el repo en GitHub creado o lo creamos desde cero?
