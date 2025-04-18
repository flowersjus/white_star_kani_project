# Characters Directory

This folder contains all primary characters for the White Star solo campaign, including the player character and major recurring NPCs.

## Structure

Each character is stored in its own JSON file, e.g. `jax_varn.json`. Character files may include the following fields:

```json
{
  "name": "Jax Varn",
  "class": "Mercenary",
  "race": "Human",
  "level": 3,
  "hp": 16,
  "max_hp": 18,
  "credits": 85,
  "inventory": ["Laser Pistol", "Energy Cell (x6)", "Med Kit"],
  "status": "Active"
}
```

## Summary Cards

The `summary_cards/` subfolder is used to store single-page versions of character sheets, optimized for display in tools like Kani or for printing.

## Notes

- All character files are manually maintained, though tools may eventually write to or read from them.
- Temporary companions or factions may be stored in a `npcs/` folder instead of here.
- Optional fields like `background`, `traits`, `goals`, or `session_notes` are supported but not required.
