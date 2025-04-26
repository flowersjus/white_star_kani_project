# Skill Check System Guide

## Overview

The skill check system provides a consistent mechanic for resolving uncertain actions in the White Star RPG. It uses a d20 roll plus an attribute modifier, compared against a Difficulty Class (DC).

## When to Use Skill Checks

Skill checks should be used when:

- There is **meaningful risk or reward**
- The outcome is **uncertain** (not obvious)
- The task is **extraordinary**, **dangerous**, or **resisted**

Do **not** use skill checks when:

- The action is simple/common and risk-free
- The character would logically succeed without challenge

## How to Call a Skill Check

In the game, the AI Game Master will automatically call for skill checks when appropriate. Players can also request skill checks for specific actions.

### Function Syntax

```
/skill_check <character> <attribute> <difficulty> <description>
```

### Parameters

- **character**: The character's name
- **attribute**: The attribute to use (strength, intelligence, wisdom, constitution, dexterity, charisma)
- **difficulty**: The difficulty class (DC) to beat (default: 14 - Average)
- **description**: Optional description of what the character is attempting

### Example Usage

```
/skill_check "Jax Varn" strength 14 "force open the airlock door"
```

## Difficulty Classes

| Difficulty | DC | Example Tasks |
|:-----------|:---|:--------------|
| Easy       | 10 | Climbing a ladder, recalling common knowledge |
| Average    | 14 | Climbing a steep wall, hacking a standard terminal |
| Hard       | 18 | Climbing a smooth surface, hacking a secure system |
| Very Hard  | 22 | Climbing a slick, overhanging surface, hacking a military system |
| Nearly Impossible | 26 | Climbing a ceiling, hacking an alien AI |

## Attribute Guidelines

Choose the appropriate attribute for the task:

- **Strength**: Physical force, lifting, breaking, melee attacks
- **Intelligence**: Knowledge, memory, reasoning, technical skills
- **Wisdom**: Perception, intuition, willpower, survival
- **Constitution**: Endurance, stamina, resisting physical effects
- **Dexterity**: Agility, balance, stealth, ranged attacks, reflexes
- **Charisma**: Social interaction, leadership, deception, intimidation

## Outcomes

| Roll Result | Outcome |
|:------------|:--------|
| Natural 1 (unmodified) | Critical Failure (automatic) |
| Natural 20 (unmodified) | Critical Success (automatic) |
| Total ≥ DC | Success |
| Total < DC | Failure |

### Interpreting Results

- **Critical Success**: The character achieves exceptional results beyond a normal success. This might include additional benefits, faster completion, or bonus effects.
- **Success**: The character accomplishes the action as intended.
- **Failure**: The character fails to accomplish the action, with normal consequences.
- **Critical Failure**: Something goes wrong beyond a simple failure. This might include complications, damage, or other negative consequences.

## Passive Checks

For situations where a character might notice something without actively searching, use passive checks:

Passive check = 10 + attribute modifier

This is particularly useful for:
- Spotting hidden dangers
- Noticing ambushes
- Detecting subtle environmental changes

## Example Scenarios

| Scenario | Attribute | Typical DC |
|:---------|:----------|:-----------|
| Forcing open a jammed door | Strength | 14 |
| Recalling information about an alien species | Intelligence | 14 |
| Noticing a hidden surveillance device | Wisdom | 16 |
| Enduring extreme cold without protection | Constitution | 16 |
| Slipping past a security drone | Dexterity | 18 |
| Convincing a guard to let you pass | Charisma | 14 |

## Integration with Other Mechanics

- **Combat**: Continue to use attack rolls for combat actions
- **Saving Throws**: Use saving throws for resisting effects
- **Skill Checks**: Use for ability-based challenges outside of combat

## Tips for Game Masters

- Only call for checks when the outcome is uncertain and meaningful
- Set appropriate DCs based on the difficulty of the task
- Consider giving advantage (roll twice, take higher) for favorable circumstances
- Consider giving disadvantage (roll twice, take lower) for unfavorable circumstances
- Be consistent in how you apply skill checks
- Describe the results narratively, not just mechanically

## Tips for Players

- Describe your actions in detail to give the GM context
- Think about which attribute would be most appropriate for your action
- Consider the environment and your character's abilities when attempting actions
- Accept failures as part of the narrative and use them to drive the story forward
