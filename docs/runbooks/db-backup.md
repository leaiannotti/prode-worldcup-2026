# Database Backup Runbook

Living documentation of the database backup setup for `prode-worldcup-2026`.

> If you change the backup configuration, update this document in the same PR.

---

## Architecture

| Item | Value |
|---|---|
| Hosting platform | Coolify v4.1.2 (self-hosted on DigitalOcean droplet) |
| Backup destination | DigitalOcean Spaces (S3-compatible) |
| Spaces region | `SYD1` |
| Spaces bucket | `prode-coolify-backups` |
| Spaces endpoint | `https://syd1.digitaloceanspaces.com` |
| Backup format | PostgreSQL custom format (`.dmp` via `pg_dump -Fc`) |
| Encryption at rest | Spaces default (AES-256, managed by DO) |

### What gets backed up

| Database | Why | Frequency | Local retention | S3 retention |
|---|---|---|---|---|
| `prode-worldcup` app database | User predictions, scores, accounts | Daily 03:00 SYD1 | 1 day | 30 days |
| Coolify internal database | Coolify config, secrets, app definitions | Daily 04:00 SYD1 | 1 day | 30 days |

Schedules are offset by one hour to avoid disk and network contention on the droplet.

### Why short local retention

The droplet has a single 50 GB volume shared between OS, Docker, live databases, and backups. Local retention is intentionally kept at the Coolify minimum (1 day) so backups never threaten production disk space. The authoritative copy lives in Spaces.

This follows the 3-2-1 rule: live DB on the droplet volume, fresh backup on the droplet volume short-term, durable backup in Spaces off-site.

---

## Configuration locations

### S3 Storage entry in Coolify

**Coolify UI → Sidebar → Storages → `do-spaces-backups`**

| Field | Value |
|---|---|
| Name | `do-spaces-backups` |
| Endpoint | `https://syd1.digitaloceanspaces.com` |
| Region | `syd1` |
| Bucket | `prode-coolify-backups` |
| Access Key | (managed in DO Spaces Keys, see "Key rotation" below) |
| Secret Key | (managed in DO Spaces Keys, see "Key rotation" below) |

### App database backup

**Coolify UI → Project `prode-worldcup-2026` → PostgreSQL resource → Tab "Backups"**

| Field | Value |
|---|---|
| Enabled | ON |
| Frequency (cron) | `0 3 * * *` |
| Retention local | 1 day |
| Save to S3 | ON → `do-spaces-backups` |
| Retention S3 | 30 days |
| Databases | `all` |

### Coolify internal database backup

**Coolify UI → Settings → Backup**

| Field | Value |
|---|---|
| Backup Coolify Database | ON |
| S3 Storage | `do-spaces-backups` |
| Frequency | `0 4 * * *` |
| Retention local | 1 day |
| Retention S3 | 30 days |

---

## Verifying backups are running

Without downloading anything. Do this at least once a week.

### Quick check from the DO panel

1. Open **DigitalOcean → Spaces → `prode-coolify-backups`**.
2. Sort by **Last Modified** descending.
3. Confirm there is one `.dmp` for the app database dated within the last 24 hours.
4. Confirm there is one `.dmp` for the Coolify internal database dated within the last 24 hours.

If either is missing or stale, check Coolify notifications (see [`Alerts`](#alerts) below) and the backup history tab inside Coolify for the resource that failed.

### Check from Coolify UI

- **Project → PostgreSQL → Backups tab**: shows last N runs with timestamp and status.
- **Settings → Backup**: shows last run of the internal Coolify DB backup.

A green status row plus a matching object in Spaces means the backup is healthy.

---

## Alerts

**Coolify UI → Settings → Notifications**

The following events should be enabled at minimum:

- `Backup Failed` — required.
- `Backup Successful` — recommended for the first month, then optional.

The configured channel for this project is documented privately (Discord/Telegram/email). Do not commit channel tokens to the repo.

### Validating alerts work

Schedule this as a quarterly task. Do not do it ad hoc against production credentials.

1. In DO, rotate the Spaces key used by Coolify but do NOT update Coolify yet.
2. Trigger a manual backup from Coolify UI → it should fail.
3. Confirm the failure notification arrives in the configured channel.
4. Update Coolify with the new key (see "Key rotation" below).
5. Run another manual backup → must succeed.

---

## Key rotation

Spaces Access Keys should be rotated at least every 12 months or immediately if compromise is suspected.

### Procedure

1. **DO Panel → API → Spaces Keys → Generate New Key**
   - Name: `coolify-backups-<YYYY-MM>`
   - Save Access Key and Secret Key.
2. **Coolify UI → Storages → `do-spaces-backups` → Edit**
   - Replace Access Key and Secret Key with the new pair.
   - Click **Validate Connection** → must be green.
3. **Run a manual backup** from any database resource using this storage to confirm uploads still work.
4. **DO Panel → API → Spaces Keys → delete the old key**.
5. Update this runbook only if the key name format changes.

---

## Changing retention

### Local retention

Increase only if you have headroom on the 50 GB droplet volume. Check first:

```bash
df -h /
docker system df
```

If `/` is below 70 % used and Docker volumes are stable, 3 days of local retention is safe. Do not exceed 7 days without moving to a separate Block Storage volume.

### S3 retention

Change in the same Coolify Backup configuration screens. 30 days is the current default; cost scales linearly. As of writing, DO Spaces is a flat ~$5/month up to 250 GB stored.

For longer retention without proportional cost, configure a Spaces lifecycle rule to move objects to a cheaper class or to delete after N days — managed in the DO Spaces UI, not in Coolify.

---

## Restore

See [`db-restore.md`](./db-restore.md). Do not improvise a restore — follow the runbook.

---

## Change log

| Date | Change | Author |
|---|---|---|
| Initial setup | Backup pipeline established with DO Spaces in SYD1 | — |
