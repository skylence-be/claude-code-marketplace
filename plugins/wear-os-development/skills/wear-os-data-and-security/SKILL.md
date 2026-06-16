---
name: wear-os-data-and-security
description: Wear OS data persistence, Data Layer sync, networking, security, and battery-aware background work. Use when storing or syncing watch data.
category: wear-os
tags: [wear-os, datastore, data-layer, security, keystore, background-work, battery]
related_skills: [wear-os-blueprint, wear-os-health-services, wear-os-compose-patterns]
---

# Wear OS Data, Sync & Security

How to persist, sync, secure, and schedule data on a watch — where battery and a tiny
Bluetooth pipe make the wrong choice expensive.

## Persistence — use DataStore (NOT EncryptedSharedPreferences)

**`androidx.security:security-crypto` (EncryptedSharedPreferences / EncryptedFile) is
DEPRECATED** as of its stable `1.1.0` release — there will be **no further releases**.
Do not start new code on it.

Use **Jetpack DataStore** (`androidx.datastore`):

| Variant | Stores | When |
|---------|--------|------|
| Preferences DataStore | key/value | simple flags, settings |
| Proto DataStore | typed objects (protobuf) | structured records (e.g. RunRecord) |

```kotlin
val Context.settings: DataStore<Preferences> by preferencesDataStore("settings")
suspend fun setUnits(metric: Boolean) {
    context.settings.edit { it[booleanPreferencesKey("metric")] = metric }
}
val unitsFlow = context.settings.data.map { it[booleanPreferencesKey("metric")] ?: true }
```

- DataStore is coroutine/Flow based, transactional, and async — no blocking disk I/O.
- Migrate off EncryptedSharedPreferences with `SharedPreferencesMigration`.

## Security & secrets

- **Android Keystore** stores key material (hardware-backed where available); use it to
  hold keys, not to bulk-encrypt data.
- Use **Tink** (Google's crypto library) to encrypt/decrypt payloads with a Keystore-held
  key, then persist the **ciphertext** in DataStore or a file.
- **Credential Manager** for sign-in on the watch (don't reuse phone-only auth UIs).
- Follow the Android security checklist: least-privilege permissions, never log secrets,
  validate all inbound Data Layer messages.

## Phone ↔ watch sync — Data Layer API

`com.google.android.gms:play-services-wearable` provides the Data Layer (part of Google
Play services):

| Client | Use |
|--------|-----|
| `DataClient` | sync small `DataItem`s across nodes |
| `MessageClient` | fire-and-forget `MessageEvent`s |
| `CapabilityClient` | discover which nodes have a feature / app installed |
| `ChannelClient` | stream larger payloads |

- Over Bluetooth it's a single encrypted channel; when BT is down, data routes
  end-to-end-encrypted via Google Cloud.
- **Do NOT use the Data Layer to reach the internet** — BLE bandwidth can be ~4 KB/s and
  DataItems are meant to be small.
- Use `WearableListenerService` for events when the app may be closed; register a **live
  listener** instead if you only need events while active (saves battery).

## Networking (standalone)

Standalone watches go **directly to the network** (Retrofit/OkHttp/`HttpURLConnection`),
not through the phone. Wrap non-urgent network sync in WorkManager.

## Background work & battery

- **WorkManager** (`androidx.work:work-runtime-ktx`) for deferrable/periodic work — it is
  battery-aware and respects Doze. Don't schedule too often; add constraints like
  `RequiresCharging` for non-urgent sync.
- **Foreground service + Ongoing Activity** for user-visible long tasks (tracking, media).
- Avoid wake locks; avoid always-on unless the use case justifies the battery cost.

## Do / Don't

- ✅ DataStore for persistence; Keystore + Tink for secrets.
- ✅ Data Layer for small phone↔watch state; direct network for the internet.
- ✅ WorkManager with constraints for sync.
- ❌ EncryptedSharedPreferences in new code (deprecated, no future releases).
- ❌ Data Layer API as a network transport.
- ❌ Frequent/always-on background work that drains the battery.
