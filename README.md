[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![GitHub stars](https://img.shields.io/github/stars/AK-O/plant_care?style=social)](https://github.com/AK-O/plant_care/stargazers)

# Plant Care Integration (Home Assistant)

A Home Assistant custom integration to manage  **watering** ,  **fertilizing** , and optional **plant environment monitoring**  **per plant** .

* ✅ One config entry = one plant
* ✅ Entity-driven (HA-native, automation-friendly)
* ✅ Optional environment sensors (no noise if you don’t configure them)
* ❌ No built-in notifications (use automations)

---

## Table of Contents

* [Features](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#features)
* [Installation](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#installation)
* [Configuration](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#configuration)
* [Entities](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#entities)
* [How It Works](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#how-it-works)
* [Automations (YAML Examples)](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#automations-yaml-examples)
* [Update Behavior](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#update-behavior)
* [FAQ](https://chatgpt.com/c/69582127-1f64-8326-97df-99677fc2b078#faq)

---

## Features

### Task Tracking

Per plant:

* Watering schedule (interval-based)
* Fertilizing schedule (interval-based)
* “Mark done” buttons
* Due / overdue status (binary sensors + attributes)

### Environment Monitoring (Optional)

Per plant (if you assign external sensors):

* Temperature / humidity / soil moisture monitoring
* Out-of-range binary sensors (`device_class: problem`)
* Deviation sensors (how far outside the target range)

---

## Installation

> This integration is intended to be installed like any other custom Home Assistant integration.

### Option A: HACS (recommended)

1. Add this repository to HACS as a **custom repository** (type: Integration)
2. Install **Plant Care Integration**
3. Restart Home Assistant

### Option B: Manual

1. Copy the integration folder into:
   `config/custom_components/plant_care/`
2. Restart Home Assistant

---

## Configuration

### Add a Plant

1. Go to **Settings → Devices & services**
2. Click **Add Integration**
3. Search for **Plant Care Integration**
4. Enter a **Plant Name** (e.g. `Monstera Deliciosa`)

This creates:

* **One device per plant**
* A stable `<plant_id>` derived from the name using slugify (e.g. `monstera_deliciosa`)

Renaming the plant later changes friendly names, but  **entity IDs remain stable** .

### Configure Options

All configuration is done via entities and options:

* Intervals and targets are exposed as **Number entities**
* Optional external sensors can be assigned in the plant device **options**

---

## Entities

Each plant device exposes the following entities.

### Quick Reference (All Entities)

#### Numbers (Settings)

* `number.<plant_id>_watering_interval_days` (0…60)
* `number.<plant_id>_fertilizing_interval_days` (0…365)
* `number.<plant_id>_moisture_min` / `number.<plant_id>_moisture_max` (0…100)
* `number.<plant_id>_humidity_min` / `number.<plant_id>_humidity_max` (0…100)
* `number.<plant_id>_temp_min` / `number.<plant_id>_temp_max` (-10…50, step 0.5)
* `number.<plant_id>_light_min` / `number.<plant_id>_light_max` (0…100000, informational)

#### Buttons (Actions)

* `button.<plant_id>_watering_mark_watered`
* `button.<plant_id>_fertilizing_mark_fertilized`

#### Binary Sensors (Tasks)

* `binary_sensor.<plant_id>_watering_due`
* `binary_sensor.<plant_id>_fertilizing_due`

Attributes on task sensors:

* `next_due_date`
* `days_overdue`

#### Sensors (Task Diagnostics)

* `sensor.<plant_id>_watering_last`
* `sensor.<plant_id>_watering_next`
* `sensor.<plant_id>_fertilizing_last`
* `sensor.<plant_id>_fertilizing_next`

#### Binary Sensors (Environment Problems)

(only meaningful if external sensors are assigned)

* `binary_sensor.<plant_id>_temperature_out_of_range`
* `binary_sensor.<plant_id>_humidity_out_of_range`
* `binary_sensor.<plant_id>_moisture_out_of_range`

#### Sensors (Environment Deviation)

* `sensor.<plant_id>_temperature_deviation`
* `sensor.<plant_id>_humidity_deviation`
* `sensor.<plant_id>_moisture_deviation`

Deviation behavior:

* `0.0` → value is within bounds
* `> 0` → value is outside bounds
* `unavailable` → no sensor configured / invalid sensor value

---

## How It Works

### Core Rules (Watering & Fertilizing)

#### Disable a task

If interval is `0`:

* task is disabled
* due sensor is `off`
* next due date is `None`
* no overdue calculation

#### Enable a task

If interval is `> 0`:

* If never done before: task is **immediately due**
* If done before: next due date = `last_done + interval_days`
* Due when `today >= next_due_date`

### External Sensors (Optional)

You may assign these in the plant device options:

* temperature sensor
* humidity sensor
* soil moisture sensor

If you don’t assign a sensor:

* related entities are disabled by default
* values show `unavailable`
* out-of-range sensors won’t create false alerts

---

## Automations (YAML Examples)

> Tip: These examples use `notify.mobile_app_phone`. Replace it with your notifier (e.g. `notify.notify`, `notify.mobile_app_<device>`, etc.).

### 1) Notify when watering is due

```yaml
alias: "Plant - Monstera needs watering"
description: "Send a notification when Monstera watering becomes due"
trigger:
  - platform: state
    entity_id: binary_sensor.monstera_deliciosa_watering_due
    to: "on"
action:
  - service: notify.mobile_app_phone
    data:
      message: "Monstera needs watering 🌱"
mode: single
```

### 2) Include overdue days in the message

```yaml
alias: "Plant - Watering overdue message"
trigger:
  - platform: state
    entity_id: binary_sensor.monstera_deliciosa_watering_due
    to: "on"
action:
  - service: notify.mobile_app_phone
    data:
      message: >-
        Monstera needs watering 🌱
        Overdue: {{ state_attr('binary_sensor.monstera_deliciosa_watering_due', 'days_overdue') }} day(s)
mode: single
```

### 3) Notify when temperature is out of range

```yaml
alias: "Plant - Temperature out of range"
trigger:
  - platform: state
    entity_id: binary_sensor.monstera_deliciosa_temperature_out_of_range
    to: "on"
action:
  - service: notify.mobile_app_phone
    data:
      message: >-
        Monstera temperature is out of range 🌡️
        Deviation: {{ states('sensor.monstera_deliciosa_temperature_deviation') }}
mode: single
```

### 4) Disable fertilizing for a plant

```yaml
service: number.set_value
target:
  entity_id: number.monstera_deliciosa_fertilizing_interval_days
data:
  value: 0
```

### 5) Notify on **any** plant problem (one automation)

This automation listens to *all* `state_changed` events and notifies you when any Plant Care **problem** binary sensor turns `on`.

> ✅ Includes task due sensors and out-of-range sensors.
> ❗ Replace `notify.mobile_app_phone` with your notifier.

```yaml
alias: Plant Care - Notify on any problem
description: ""
mode: queued

trigger:
  - platform: event
    event_type: state_changed

condition:
  - condition: template
    value_template: >
      {% set e  = trigger.event.data.entity_id %}
      {% set ns = trigger.event.data.new_state %}
      {% set os = trigger.event.data.old_state %}
      {{ e is string
         and e.startswith('binary_sensor.')
         and ns is not none
         and ns.state == 'on'
         and (os is none or os.state != 'on')
         and ns.attributes.get('device_class') == 'problem'
         and (
           e.endswith('_watering_due')
           or e.endswith('_fertilizing_due')
           or e.endswith('_temperature_out_of_range')
           or e.endswith('_humidity_out_of_range')
           or e.endswith('_moisture_out_of_range')
         )
      }}

action:
  - service: notify.mobile_app
    data:
      title: Plant Care
      message: >
        {% set ns = trigger.event.data.new_state %}
        🚨 {{ ns.name }}
        {% set attrs = ns.attributes %}
        {% if attrs.get('next_due_date') %} Next due: {{ attrs.get('next_due_date') }}{% endif %}
        {% if attrs.get('days_overdue') is not none %} Overdue: {{ attrs.get('days_overdue') }} day(s){% endif %}
        {% if attrs.get('deviation') is not none %}
          {% set dev = attrs.get('deviation') | float(default=none) %}
          {% if dev is not none %} Deviation: {{ dev | round(2) }}{% else %} Deviation: {{ attrs.get('deviation') }}{% endif %}
        {% endif %}

```

---

## Update Behavior

The coordinator recalculates:

* Every **15 minutes** (environment monitoring)
* Daily at **03:00**
* Immediately when:
  * a button is pressed
  * a number setting changes

---

## FAQ

### Why no notifications?

Home Assistant users typically want full control over notification channels, schedules, and quiet hours. This integration exposes  **state** , and you decide what happens via automations.

### Why are some entities disabled by default?

Environment entities are disabled by default when no external sensors are assigned to avoid noise and “unavailable” clutter.

### Will renaming a plant break entity IDs?

No. Friendly names change, but `<plant_id>` stays stable.

---

## ❤️ Support

If this Home Assistant integration is useful to you and saves you time, you can support its development:

☕ **Buy me a coffee:** https://buymeacoffee.com/ako_

Starring the repository ⭐ and reporting issues or improvements are also great ways to help.
