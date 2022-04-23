# Boring Details

This file is supposed to give some more details on the workings of the scripts in this repository.  
The general README is titled [README.md](README.md), read that one first if you didn't already. It also includes a link to a bigger coding guide for Blender I made (currently inlcudes almost 100 pages!).

## Imports
When any of the scripts in this repository import another one, you will see that it uses a **relative** import for that.  
Among other things, this basically means I use dots instead of the parent folder name in imports.  
So for instance instead of  
`from toolbox import delete_stuff`, you will see  
`from . import delete_stuff`  

This is **on purpose**, because it allows you to make this folder part of other stuff (like add-ons) without having to change any of the import statements yourself, and everything will (or should) still work.  
I found that absolute paths give problems in add-ons.

However, this means that when you want to open a particular script (that uses relative imports) inside the Blender text editor directly, you must have it enable relative imports first with some additional code. I actually even made a post on stackexchange on that: https://blender.stackexchange.com/a/255605/87805  
For this purpose, the following code is included in any such scripts at the beginning of the file:

```
import sys
import pathlib


#enable relative imports:
if __name__ == '__main__': #makes sure this only happens when you run the script from inside Blender
    
    # INCREASE THIS VALUE IF YOU WANT TO ACCESS MODULES IN PARENT FOLDERS (for using something like "from ... import someModule") 
    number_of_parents = 1 # default = 1
    
    original_path = pathlib.Path(bpy.data.filepath)
    parent_path = original_path.parent
    
    for i in range(number_of_parents):
        parent_path = parent_path.parent
    
    
    str_parent_path = str(parent_path.resolve()) # remember, paths only work if they're strings
    #print(str_parent_path)    
    if not str_parent_path in sys.path:
        sys.path.append(str_parent_path)

    # building the correct __package__ name
    relative_path = original_path.parent.relative_to(parent_path)
    with_dots = '.'.join(relative_path.parts)
    #print(with_dots)
    __package__ = with_dots
```
If you want to open one of my scripts directly inside Blender but get this:
> "ImportError: attempted relative import with no known parent package"

It very likely means that the script uses a relative import and I forgot to add the code above.

Hint:  
Another method that I don't use anymore, but still want to tell you about is this:
https://blender.stackexchange.com/questions/51044/how-to-import-a-blender-python-script-in-another  

1. Open all the scripts (main one and the ones to be imported) in the Blender Text Editor
2. instead of writing something like "import yourScript", write yourScript = bpy.data.texts["yourScript.py"].as_module()
3. It now works as if it had been imported
  
## What area do you call these functions from?
A big part of Blender logic is the context (`bpy.context` or often shortened to just `C`)    
Did you know that that includes the type of window you're currently "inside" of? For instance, if you type `print(bpy.context.area.type)` in    
- a blender console, you will see `'CONSOLE'`
- a blender text editor, you will see `'TEXT_EDITOR'`
- if you create a blender operator (often done in add-ons) with the code above, add a button to the "Object Properties" panel that calls that operator, and click it, you will see `'PROPERTIES'`     

I'm telling you this information because, **depending on your current area type, some things might not work with your code**. Some (but only a few) of the functions in this repository even have warnings about this in their descriptions.      

An example is my `select_objects` function: I ran into a situation where, after doing certain changes to scenes, I suddenly couldn't select an object when I had the area type `'PROPERTIES'` active. It turned out that bpy.context.view_layer somehow got messed up and took the value of a view_layer of another scene instead of the one that was currently active, and selecting objects depended on those view_layers being correct.    
This problem did **not** appear if the area type was one of `CONSOLE`, `TEXT_EDITOR` or `VIEW_3D`, only with `'PROPERTIES'`
From doing some testing I found that the best way to prevent those bugs is to simply change the context area type to one that works before you run your unstable code. It's actually fairly easy, you literally only need to change the `.type` property.    
So for example:
```
old_area_type = C.area.type
C.area.type = "CONSOLE"
select_objects(x,y,z) # do your code
C.area.type = old_area_type
```

Be aware however to not overdo this, as changing the area type very often might actually take some time to compute, although that's just a guess - I never actually tested its time efficiency.

To end this, I found that the following area types **did not** lead to any problems in my test code:
- `'CONSOLE'`
- `'TEXT_EDITOR'`
- `'VIEW_3D'` (maybe try the other types first if you run into problems, because this one *might* make everything in your code slower)

The following area types **did** lead to problems:
- `'PROPERTIES'`


## __Things starting with two underscores
You will see that at some locations, my variables or function will start with two underscores (but not also end with two underscores, those are different, special "magic" functions or attributes):
```
__some_variable = 4
def __some_function():
    return "hello"
```
Most often they will appear in some of my classes.
```
class SomePerson():
    name = "Joe"
    __loves_his_partner = True
    age = "41"

    def __check_if_he_still_loves_his_partner():
        ...
```

This basically marks those functions or attributes with:
>"I'm not supposed to be touched by outsiders, please leave me alone."

Which in other words means the code in the respective scripts needs to use them, but your script shouldn't, because of one or multiple of the following reasons:
- **__attributes**:
    - The attribute contains data you already know
    - The attribute contains data that's useless for you
    - The attribute contains data you shouldn't change because you might mess stuff up 
- **__functions**:
    - The function does stuff that's useless for you
    - The function does stuff in such a special cut way that it isn't good for general use and I don't even want you to consider using it instead of using or creation a better version

A nice feature is that many code editors don't show you those attributes/functions when displaying what you can use from a class, keeping what you see "clean" of uneccessary information.  
(If you don't know what I'm talking about, go into Blender, write into the python console "*C.scene.*" and press TAB. You will now see a bunch of attributes and functions you can use from that C.scene)

Hint: Accessing, although obviously discouraged, is still possible although you will need to use special variations of their names.  
This whole thing with using underscores is called *"Name Wrangling"* and here are two example articles about it if you want to know more:  
https://stackoverflow.com/questions/1301346/what-is-the-meaning-of-single-and-double-underscore-before-an-object-name  
https://docs.python.org/3/tutorial/classes.html#private-variables

Sometimes you might also see one underscore being used instead of two in my code, that's because of some naming problems.