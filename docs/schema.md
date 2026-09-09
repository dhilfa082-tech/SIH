# AgriLink AI Database Schema

## 1. Farmer
- farmer_id
- name
- phone
- location

## 2. Produce
- produce_id
- farmer_id
- crop_name
- quantity_kg
- location
- availability_date
- status

## 3. Buyer
- buyer_id
- buyer_name
- crop_name
- required_quantity_kg
- location
- urgency

## 4. Pool
- pool_id
- crop_name
- total_quantity_kg
- location
- pool_status

## 5. Journey Log
- journey_id
- produce_id
- current_status
- timestamp

Journey Stages:

Produce Registered
→ Farmer Pool Created
→ Bulk Lot Created
→ Buyer Matched
→ Destination Confirmed
→ Transport Assigned
→ In Transit
→ Delivered
→ Payment Status
