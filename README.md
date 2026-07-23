# 🚀 Deep Space Invasion

**Version 2.0.1**

A 2D arcade-style space shooter built with **Python** and **Pygame** featuring multiple enemy types, boss battles, pixel-perfect collision detection, original pixel art, and sound effects.

## Features

- Player-controlled spaceship
- Multiple enemy ship types
- Three unique boss encounters (one every 10 levels)
- Pixel-perfect collision detection using Pygame masks
- Health bars for player and bosses
- Sound effects
- Original pixel-art sprites
- Object-oriented game architecture
- Interactive menu buttons and UI elements

## Technologies

- Python 3
- Pygame

## Programming Concepts Demonstrated

- Object-Oriented Programming (OOP)
- Inheritance
- Encapsulation
- Event-driven programming
- Collision detection
- Game loop architecture
- Modular programming

## How to play

- The player starts with a ship which they can move using WASD or the arrow keys.
- Enemy ships will appear which the player can shoot using the space bar.
- If an enemy ship reaches the end of the screen the player will lose one of their five lives.
- If the player collides with an enemy ship, or is hit by an enemy laser, they will lose health.
- If the player's health reaches 0 or they lose all 5 lives they will lose the game and return to the main menu.
- Every 5 levels, the player regains 20% of their health.
- Every 10 levels, the player's health is restored.
- The game is separated into 30 levels; if the player completes level 30 they win.
- There are 3 bosses total — one encountered every 10 levels.

## Difficulty curve

- At the start of level 5, enemy ships will begin to swerve, making them harder to hit. Every 5th level the swerve will gradually grow greater.
- The enemies' velocity increases at the start of each new level by 0.1.
- To account for this, the player's velocity increases by 0.15 each level.
- Each level will also contain one more enemy in the wave.
- Every 10th level the enemies' fire rate will increase.
- To balance this, the player's cooldown rate will decrease every 5th level until it reaches 1/6 seconds.

## Installation

```bash
pip install pygame
python main.py
```

## Future Improvements

- Additional enemy types
- Power-ups
- High score system
- Save system
- Additional bosses

## What I Learned

This project strengthened my understanding of object-oriented programming, reusable class design, collision systems, game state management, and integrating graphics and audio into a complete application.
