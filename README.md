# Fake Space-Invaders

### How to play
The player stars with a ship which they can move using WASD or the arrow keys.
Enemy ships will appear which the player can shoot using the space bar.
If an enemy ship reaches the end of the screen the player will lose one of their five lives.
If the player collides with an enemy ship, or is hit by and enemy laser, they will lose health.
If the players health reaches 0 or they lose all 5 lives they will lose the game and return to the start screen.
Every 5 levels, the players health is restored.
The game is seperated into 30 levels, if the player completes level 30 they win.

### Difficulty curve
At the start of level 5 ships will begin to swerve making them harder to hit. Every 5th level the swerve will gradually grow greater and greater. 
The enemies velocity will also increase with the start of each new level by .1. To account for this, the players velocity will increase by .2.
Each level will also contain one more enemy in the wave.
Every 10nth level the enemies fire rate will increase, to account for this, the players cooldown rate will decrease every 5th level until it reaches 1/6 seconds.
