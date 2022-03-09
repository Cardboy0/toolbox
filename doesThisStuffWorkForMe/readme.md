# Check if the functions of this repository work for you

If you stumbled across this repository, you might want to use some of those functions and classes for your own projects.
However you might be unsure if they still work, or even just if they work on your specific environment.  
In that case you can use the .py script in this specific subfolder to do a quick check - it does a bunch of tests with (almost) all other script contents in this repository to check if they still work.

## How do I test?
There are two ways:  
#1: Running the test script directly:
1. Create a new empty Blender Project **inside this subfolder**
2. Open the **checkFunctionality.py** script in that project.
3. Run it
4. Check the console for any print statements or raised exceptions.
  
#2: Running as part of an add-on
1. Simply import the module and run the `run()` function (in an Operator or something similar)
2. The run() function returns True when everything succeeded or False if not.

## What repository???
If, for some reason, this readme file exists as a lone file on your computer, or the parent folder disappeared:
It's part of the "**toolbox**" repository (development by me, Cardboy0), which you can find at 
https://github.com/Cardboy0/toolbox along with more information

