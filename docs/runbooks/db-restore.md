# Database Restore Runbook

Procedure to restore a PostgreSQL database for `prode-worldcup-2026` from a backup stored in DigitalOcean Spaces.

> Read this entire document before starting a restore. Improvising during an outage corrupts data.

---

## When to use this runbook

| Scenario | Section |
|---|---|
| Production app database lost or corrupted | [App database restore](#app-database-restore) |
| Coolify itself broken or reinstalled | [Coolify internal database restore](#coolify-internal-database-restore) |
| Need to inspect a backup without affecting production | [Sandbox restore](#sandbox-restore-non-destructive) |
| Routine monthly verification | [Sandbox restore](#sandbox-restore-non-destructive) |

---

## Pre-flight checklist

Before touching anything, confirm:

- [ ] You have the latest `.dmp` file or know exactly which one to restore.
- [ ] You have `pg_restore` available locally (`postgresql-client` package or Docker image).
- [ ] You have credentials to access Spaces (`s3cmd`, `aws-cli`, or DO panel).
- [ ] You have notified the team in the agreed channel that a restore is in progress.
- [ ] You have a window where users can be impacted (for production restores).
- [ ] You have the current production `DATABASE_URL` for the target database.

If any item is unchecked, stop and resolve it first.

---

## Downloading a backup from Spaces

### Option 1 — DO Panel (manual, GUI)

1. **DO Panel → Spaces → `prode-coolify-backups`**.
2. Sort by **Last Modified** descending.
3. Identify the correct `.dmp` (see naming conventions in [`db-backup.md`](./db-backup.md)).
4. Right-click → **Download**.

### Option 2 — `s3cmd` (scriptable)

```bash
s3cmd --host=syd1.digitaloceanspaces.com \
      --host-bucket='%(bucket)s.syd1.digitaloceanspaces.com' \
      --access_key=$DO_SPACES_KEY \
      --secret_key=$DO_SPACES_SECRET \
      ls s3://prode-coolify-backups/

s3cmd --host=syd1.digitaloceanspaces.com \
      --host-bucket='%(bucket)s.syd1.digitaloceanspaces.com' \
      --access_key=$DO_SPACES_KEY \
      --secret_key=$DO_SPACES_SECRET \
      get s3://prode-coolify-backups/<filename>.dmp ./backup.dmp
```

Never hardcode the credentials in a script. Export them in your shell session and unset them after.

---

## Validating the backup before restoring

Always do this before pointing `pg_restore` at production.

```bash
# 1. File is not zero bytes or absurdly small
ls -lh backup.dmp

# 2. pg_restore can read the catalog
pg_restore -l backup.dmp | head -30

# 3. Confirm expected tables are listed
pg_restore -l backup.dmp | grep -E "TABLE |SEQUENCE " | head -20
```

A backup that cannot list its catalog is corrupt — STOP and use the previous day's backup.

---

## Sandbox restore (non-destructive)

Use this for monthly verification or to inspect a backup. Runs entirely in Docker, never touches production.

```bash
# 1. Start ephemeral Postgres
docker run --rm -d \
  --name pg-restore-test \
  -e POSTGRES_PASSWORD=test \
  -p 5433:5432 \
  postgres:16

# 2. Wait for it to accept connections
sleep 5
docker exec pg-restore-test pg_isready -U postgres

# 3. Create target database
docker exec pg-restore-test psql -U postgres -c "CREATE DATABASE prode_restore_test;"

# 4. Restore
docker exec -i pg-restore-test pg_restore \
  -U postgres \
  -d prode_restore_test \
  --no-owner \
  --no-acl \
  --verbose \
  < backup.dmp

# 5. Smoke checks
docker exec -it pg-restore-test psql -U postgres -d prode_restore_test -c "\dt"
docker exec -it pg-restore-test psql -U postgres -d prode_restore_test \
  -c "SELECT COUNT(*) FROM users;"
docker exec -it pg-restore-test psql -U postgres -d prode_restore_test \
  -c "SELECT COUNT(*) FROM predictions;"
docker exec -it pg-restore-test psql -U postgres -d prode_restore_test \
  -c "SELECT MAX(created_at) FROM users;"

# 6. Cleanup
docker stop pg-restore-test
```

Why `--no-owner --no-acl`: the dump references the production owner role (`prode`) which does not exist in the ephemeral instance. These flags skip role-related statements so the restore completes cleanly.

**Pass criteria**:
- `\dt` lists all expected tables.
- Row counts are within reasonable range of last known production values.
- `MAX(created_at)` is close to the backup timestamp.

If any check fails, the backup is unreliable — investigate the backup pipeline, do NOT use this `.dmp` for a production restore.

---

## App database restore

**This is a destructive operation. Read the entire section before starting.**

### Step 1 — Stop the application

Coolify UI → Project `prode-worldcup-2026` → backend service → **Stop**.

This prevents writes to the database during restore. Without this step, in-flight requests will write data that gets overwritten and you will lose those records.

### Step 2 — Backup the current (broken) database

Even if the data is corrupt, capture the current state before overwriting. Forensics later may need it.

Coolify UI → PostgreSQL resource → **Backup Now** → wait for completion → confirm new `.dmp` exists in Spaces with current timestamp.

If the database is so broken that backup fails, document the error and continue — you have the daily backup as the source of truth.

### Step 3 — Validate the source backup in sandbox first

Run the entire [Sandbox restore](#sandbox-restore-non-destructive) section against the `.dmp` you intend to restore. Do NOT skip this. It takes 5 minutes and prevents catastrophic mistakes.

### Step 4 — Drop and recreate the target database

Connect to the production PostgreSQL from the droplet using the credentials in Coolify (Project → PostgreSQL → Connection Details).

```bash
# From the droplet host, via Coolify's exposed connection
psql "$DATABASE_URL_ADMIN" -c "DROP DATABASE prode_worldcup;"
psql "$DATABASE_URL_ADMIN" -c "CREATE DATABASE prode_worldcup OWNER prode;"
```

`DATABASE_URL_ADMIN` must point at the `postgres` superuser database, not at `prode_worldcup` itself (you cannot drop a database you are connected to).

### Step 5 — Restore

```bash
pg_restore \
  --host=<host> \
  --port=<port> \
  --username=prode \
  --dbname=prode_worldcup \
  --no-owner \
  --no-acl \
  --verbose \
  backup.dmp
```

Watch for errors. Non-fatal warnings about extensions or roles are expected. Fatal errors (constraint violations, missing tables) indicate the restore is incomplete — STOP and escalate.

### Step 6 — Post-restore verification

Before bringing the app back up, run these smoke queries:

```sql
-- Schema integrity
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';

-- Critical row counts
SELECT 'users' AS t, COUNT(*) FROM users
UNION ALL SELECT 'predictions', COUNT(*) FROM predictions
UNION ALL SELECT 'matches', COUNT(*) FROM matches
UNION ALL SELECT 'prediction_groups', COUNT(*) FROM prediction_groups;

-- Recency check (last write captured in backup)
SELECT MAX(created_at) AS last_user, MAX(updated_at) AS last_update FROM users;

-- Foreign key health (should return zero rows)
SELECT conname FROM pg_constraint WHERE NOT convalidated;
```

Counts should match expectations. If a critical table is empty when it should not be, STOP and investigate before continuing.

### Step 7 — Apply pending migrations (if backup is older than current code)

If the backup was taken before the currently-deployed code shipped a migration, Alembic must reapply newer migrations on top of the restored state.

```bash
# From inside the backend container
docker exec -it <backend-container> flask db upgrade
```

Check `backend/alembic/env.py` and the latest migration in `backend/migrations/versions/` to confirm there is a discrepancy. If the backup was taken minutes before the incident, this step is usually unnecessary.

### Step 8 — Restart the application

Coolify UI → backend service → **Start**.

### Step 9 — Functional smoke test

- Log in as a known user → ensure session works.
- Submit a test prediction → ensure write path works.
- Check leaderboard endpoint → ensure read path works.
- Review backend logs for the first 5 minutes → no unexpected errors.

### Step 10 — Communicate completion

Notify the team in the agreed channel:

- Restore completed at `<timestamp>`.
- Backup used: `<filename>` from `<backup-timestamp>`.
- Estimated data loss window: between `<backup-timestamp>` and `<incident-timestamp>`.
- Any anomalies observed during the restore.

---

## Coolify internal database restore

This is a disaster-recovery scenario: Coolify itself is broken or you have spun up a fresh Coolify instance and need to import the previous state.

### Step 1 — Install Coolify cleanly

Follow the official Coolify installation procedure on a fresh droplet, matching the previous version (v4.1.2 at time of writing).

### Step 2 — Stop Coolify services

```bash
cd /data/coolify/source
docker compose stop
```

### Step 3 — Identify the Coolify Postgres container

```bash
docker ps -a | grep -i coolify-db
```

The internal database container name typically is `coolify-db` but may vary by version. Confirm before continuing.

### Step 4 — Restore into the internal Postgres

```bash
# Start only the database container
docker compose up -d coolify-db
sleep 5

# Drop and recreate the database
docker exec -i coolify-db psql -U coolify -c "DROP DATABASE IF EXISTS coolify;"
docker exec -i coolify-db psql -U coolify -c "CREATE DATABASE coolify;"

# Restore
docker exec -i coolify-db pg_restore \
  -U coolify \
  -d coolify \
  --no-owner \
  --no-acl \
  --verbose \
  < coolify-internal-backup.dmp
```

### Step 5 — Start Coolify

```bash
docker compose up -d
```

### Step 6 — Verify the UI loads with previous state

Open the Coolify URL → confirm projects, servers, applications, and secrets are present.

### Step 7 — Reconnect S3 storage and verify backups still run

The Spaces credentials should already be in the restored config, but verify:

- Storages → `do-spaces-backups` → Validate Connection → green.
- Trigger a manual backup of any resource → verify upload to Spaces.

### Step 8 — Reconnect deployed applications

Each application may need to be re-pointed at its existing containers or redeployed depending on what survived the incident. This is outside the scope of this runbook — see Coolify recovery documentation.

---

## Rollback (if restore makes things worse)

If a restore introduces NEW problems and you have the pre-restore backup from Step 2 of the app restore:

1. Stop the application again.
2. Drop and recreate the target database (same as Step 4).
3. Restore from the pre-restore backup instead.
4. Restart and verify.

If you skipped Step 2, you cannot rollback — the data state from before the restore is gone. This is why Step 2 is mandatory.

---

## Common errors and fixes

| Error | Cause | Fix |
|---|---|---|
| `pg_restore: error: input file appears to be a text format dump` | File was generated with `pg_dump` plain format, not `-Fc` | Use `psql -f file.sql` instead of `pg_restore` |
| `role "prode" does not exist` | Restoring to a fresh DB without the role | Already handled by `--no-owner --no-acl`, ignore the warning |
| `extension "uuid-ossp" is not available` | Extension missing on target | `CREATE EXTENSION "uuid-ossp";` as superuser, then retry |
| `could not connect to server` during restore | Wrong host/port or DB not running | Verify connection string, ensure Postgres container is up |
| Restore hangs at "creating index" | Large table, building indexes serially | Wait — this is normal for first restore. Consider `--jobs=4` for parallel restore on next attempt |

---

## Related documents

- [`db-backup.md`](./db-backup.md) — backup configuration and verification.

---

## Change log

| Date | Change | Author |
|---|---|---|
| Initial setup | Restore runbook for app DB and Coolify internal DB | — |
