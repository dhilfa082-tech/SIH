-- ==========================
-- AgriLink AI - SIH26132
-- SQLite Schema (Prototype)
-- ==========================

PRAGMA foreign_keys = ON;

-- 1. Farmer
CREATE TABLE IF NOT EXISTS Farmer (
    farmer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    phone       TEXT NOT NULL UNIQUE,
    location    TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

-- 2. Pool  (created before Produce since Produce references it)
CREATE TABLE IF NOT EXISTS Pool (
    pool_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name         TEXT NOT NULL,
    total_quantity_kg REAL NOT NULL DEFAULT 0,
    location          TEXT NOT NULL,
    pool_status       TEXT NOT NULL DEFAULT 'open'
                      CHECK (pool_status IN ('open', 'closed', 'matched', 'completed')),
    created_at        TEXT DEFAULT (datetime('now'))
);

-- 3. Produce
CREATE TABLE IF NOT EXISTS Produce (
    produce_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id        INTEGER NOT NULL,
    pool_id          INTEGER,                       -- NULL until pooled
    crop_name        TEXT NOT NULL,
    quantity_kg      REAL NOT NULL,
    location         TEXT NOT NULL,
    availability_date TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'registered'
                      CHECK (status IN ('registered', 'pooled', 'sold')),
    created_at        TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (farmer_id) REFERENCES Farmer(farmer_id) ON DELETE CASCADE,
    FOREIGN KEY (pool_id)   REFERENCES Pool(pool_id) ON DELETE SET NULL
);

-- 4. Buyer
CREATE TABLE IF NOT EXISTS Buyer (
    buyer_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_name           TEXT NOT NULL,
    crop_name            TEXT NOT NULL,
    required_quantity_kg REAL NOT NULL,
    location             TEXT NOT NULL,
    urgency              TEXT NOT NULL DEFAULT 'normal'
                         CHECK (urgency IN ('low', 'normal', 'high')),
    created_at           TEXT DEFAULT (datetime('now'))
);

-- 5. Match  (core Buyer <-> Pool matching feature)
CREATE TABLE IF NOT EXISTS Match (
    match_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id           INTEGER NOT NULL,
    buyer_id          INTEGER NOT NULL,
    matched_quantity_kg REAL NOT NULL,
    price_per_kg      REAL,
    match_status      TEXT NOT NULL DEFAULT 'matched'
                      CHECK (match_status IN ('matched', 'confirmed', 'rejected', 'completed')),
    created_at        TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (pool_id)  REFERENCES Pool(pool_id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES Buyer(buyer_id) ON DELETE CASCADE
);

-- 6. Journey Log (generic, covers produce/pool/match stages)
CREATE TABLE IF NOT EXISTS JourneyLog (
    journey_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_type        TEXT NOT NULL CHECK (ref_type IN ('produce', 'pool', 'match')),
    ref_id          INTEGER NOT NULL,
    current_status  TEXT NOT NULL,
    timestamp       TEXT DEFAULT (datetime('now'))
);

-- ==========================
-- Helpful indexes for matching queries
-- ==========================
CREATE INDEX IF NOT EXISTS idx_produce_pool ON Produce(pool_id);
CREATE INDEX IF NOT EXISTS idx_produce_farmer ON Produce(farmer_id);
CREATE INDEX IF NOT EXISTS idx_match_pool ON Match(pool_id);
CREATE INDEX IF NOT EXISTS idx_match_buyer ON Match(buyer_id);
CREATE INDEX IF NOT EXISTS idx_journey_ref ON JourneyLog(ref_type, ref_id);
