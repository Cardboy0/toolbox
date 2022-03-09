# Boring Details

This file is supposed to give some more details on the workings of the scripts in this repository.  
The general README is titled [README.md](README.md), read that one first if you didn't already. It also includes a link to a bigger coding guide for Blender I made (currently inlcudes almost 100 pages!).

## Imports
When any of the scripts in this repository import another one, you will see that it uses a **relative** import for that.  
Among other things, this basically means I use dots instead of the parent folder name in imports.  
So for instance instead of  
`from toolbox import deleteStuff`, you will see  
`from . import deleteStuff`  

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