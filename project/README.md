##ATTACHÉ CASE

Inspired by the inventory system in the game Resident Evil 4, we decided to apply a dynamic programming approach to weapon and item distribution in an attaché case, based on their determined value. The goal was to come up with an approximation algorithm that would compare items according to their value, exchange them when necessary, and distribute them in any available space in a grid. This problem can be considered as a modified knapsack problem, where shapes are distributed on some maximum grid space instead of weights on some maximum weight limit. Through a graphical representation, our approach was to begin by adding items with the best values to the grid, or attaché case, in different trials of varying item list sizes. A “build type” was given as a parameter, with the purpose of adjusting the value of an item or weapon according to it’s class and association to the build. Weapons and items associated with a set build also have influence on other item’s values, which, for example, means that an ammunition type will have more value if the weapon that uses it is in the inventory. Our findings were that as the size of the list of items increased, the approximation algorithm was able to run in polynomial time, though the solution may not have been optimal.

###Required Libraries:

- TKinter <br>
- Numpy


###Running:
####Time Run
Running 'python project.py' will preform a time run printing the time results to the console and to a data.csv file

####GUI Run
Running 'python project.py -g' will preform a GUI run
#####Controls
- Up => move piece up
- Down => move piece down
- Left => move piece left
- Right => move piece right
- a => rotate piece clockwise
- s => rotate piece counterclockwise
- x => run placement algorithm
