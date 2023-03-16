# Check if the functions of this repository work for you

If you stumbled across this repository, you might want to use some of those functions and classes for your own projects.
However you might be unsure if they still work, or even just if they work on your specific environment.  
In that case you can use the .py script in this specific subfolder to do a quick check - it does a bunch of tests with (almost) all other script contents in this repository to check if they still work.

## How do I test?
There are two ways:  
#1: (Easy) Running the test script directly:
1. Create a new empty Blender Project **inside this subfolder**
2. Open the **run_tests.py** script in that project.
3. Run it
4. Check the console for any print statements or raised exceptions.
  
#2: (Hard) Running as part of an add-on
1. This folder has a subfolder called **test_toolbox_as_addon**
2. Copy and paste that folder into your Blender addons folder
3. The copied folder contains an **__init__.py** and another folder called **toolbox_to_test**
4. If something is already inside the **toolbox_to_test** folder, delete that stuff
5. Copy and paste the contents of the toolbox project version you want to test into the **toolbox_to_test** folder.
6. When you start Blender and check out which add-ons you can enable, **Toolbox Testing** should appear there (it's in the 'Testing' tab, not 'Official' or 'Community')
7. Enable that add-on
8. If you haven't already, open a Blender console window
9. Select any object, go to its properties panel and you should see a new sub panel called 'Test Toolbox'
10. It has a button. Click it. Wait. Check the Blender console for any output     

The add-on stuff is a bit hard to set up, and only exists to see if the methods still work if used from inside operators. There are easier alternatives to set it up, but most of them involve you having to change how Python handles the import paths, and that's not acceptable because making sure everything imports correctly WITHOUT CHANGES is one of the reasons of this testing.



## What repository???
If, for some reason, this readme file exists as a lone file on your computer, or the parent folder disappeared:
It's part of the "**toolbox**" repository (development by me, Cardboy0), which you can find at 
https://github.com/Cardboy0/toolbox along with more information

