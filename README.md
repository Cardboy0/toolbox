# toolbox
A collection of Blender Python functions and classes for frequent tasks, currently including
- **selecting objects**
- **deleting objects**
- **dealing with Collections**
- **tagging Vertices** (a.k.a. being able to track them even after their indices changed)
- **create an applied duplicate of a mesh** (a.k.a. The mesh if you would apply every shapekey, modifier etc. to it)
    - not yet properly tested
- more might follow




# testing
Because I realised that I'd rather step on a rusty nail then manually test each function or class again each time after I do some minor changes to it, I created a test script - **doesThisStuffStillWork.py**
It tries to use the other scripts in this folder for particular test cases and then simply checks the results.
You can run it inside blender and check out the console for any encountered problems.

Note: For the test script to be able to import the other scripts, you need to have all scripts open in the Blender text editor. This is kind of stupid, but means you don't need to worry about any filepath issues or save stuff.
