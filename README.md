<!-- This is a markdown file. If you can see this comment, it means that you're currently viewing the file in the wrong way. 
Visit https://markdownlivepreview.com/ and copy-paste the text in there to have it shown properly, with headings and such.-->

# toolbox
A collection of Blender Python functions and classes for frequent tasks a hobby developer might encounter, currently including
- **selecting objects**
- **duplicating objects**
- **deleting objects**
- **dealing with Collections**
- **tagging Vertices** (a.k.a. being able to track them even after their indices changed)
- **create an applied duplicate of a mesh** (a.k.a. The mesh if you would apply every shapekey, modifier etc. to it)
    - Although it seems to work, not completely tested.
- **deleting vertices, faces or edges of a mesh**
- **dealing with coordinates** (including rotation vectors)
- **dealing with keyframes (actions, fcurves)**
- **dealing with vertex groups** 
- **dealing with shape keys**
- **dealing with modifiers** (includes usage of the "bind" operator of Laplacian Deform, Surface Deform and Mesh Deform modifiers)
- **getting certain information about objects at runtime**
- some minor functions that help in testing
- Some (limited) advanced stuff:
    - **dealing with custom properties**
    - **dealing with drivers**
    - **dealing with (geometry) nodes**



- more might follow


I try to code these functions and scripts as clean as possible, including:
- proper documentation on how to use them
- great performance (*many functions use foreach_set/foreach_get methods, that are like 10 times faster than normal loops*)
- Almost never using bpy.ops (only if there's no alternative) 

**HOWEVER**, please note:
- I'm constantly adding and changing stuff, which includes renaming or moving functions. This might confuse users in some cases when they try to "update" their functions.



# source
https://github.com/Cardboy0/toolbox  
(I also have a (decentely big) guide on scripting in Blender, ranging from basis to specific and advanced topics: https://docs.google.com/document/d/1Ph6HpkmEX9KWoPC6V1UVWJ1F37qj9NkIDNQRTP-uSII)


# May I use this repository or parts of it in my own scripts?

**Personal opinion:** Yes, go ham. If I didn't want people to use this stuff, I wouldn't have made it publicly available ;-)    
But please try to always include my name (Cardboy0) and a link to this repository (https://github.com/Cardboy0/toolbox) in the stuff you copy.   

Also, while completely optional, consider sending me a message that you're using some of my stuff. It just makes me happy and provides the recognition my parents never gave me :-)

# How to download
There are two main ways to download this repository:    

**Option 1:** Visit https://github.com/Cardboy0/toolbox. Above the list of files, to the right, there should be a green button that reads "Code".
Click on it to see a dropdown menu and press the "Download ZIP" button to download it all as a zip file.

The method above will give you the most up-to-date version of this repository. If you want to download a certain previous version, do option 2 instead:

**Option 2:** Visit https://github.com/Cardboy0/toolbox/releases (or https://github.com/Cardboy0/toolbox/tags for a more compressed view) to download a certain version of this repository, like *v1.0.0*    
This might be the better choice for you because I sometimes make major changes to my files (like renaming, moving or deleting stuff, etc.) and you might come back to see that the newest version is nothing like the version you downloaded a few months ago.


(I'm just gonna assume that you know what a zip file is and how to extract it, because really, how could you have gotten this far into coding and *not* know what a zip file is?) 


# testing
- if you want to "test" the scripts in this repository - a.k.a. check if they work for you as intended - check out the **does_this_stuff_work_for_me** subfolder (there's another *readme* file inside).
- if you think you can improve a function or class, you can also do the test stuff above to check if your edited code works as intended.

# more nerdy stuff
Checkout [the other README](moreDetails.md) that explains specific stuff about this project in detail if you're confused about some things
