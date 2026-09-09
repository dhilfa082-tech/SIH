# AgriLink AI Documentation

## Database Schema

The AgriLink AI prototype uses SQLite.

### Core Tables

1. Farmer – Stores farmer information.
2. Produce – Stores produce registered by farmers.
3. Pool – Stores aggregated produce from compatible farmers.
4. Buyer – Stores buyer requirements.
5. Match – Stores matches between pooled produce and buyers.
6. JourneyLog – Tracks the journey and status of produce.

## Core System Flow

Farmer
→ Produce Registration
→ Smart Pooling
→ Buyer Matching
→ Journey Tracking
