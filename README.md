# toolbox
A collection of Blender Python functions and classes for frequent tasks a hobby developer might encounter, currently including
- **selecting objects**
- **deleting objects**
- **dealing with Collections**
- **tagging Vertices** (a.k.a. being able to track them even after their indices changed)
- **create an applied duplicate of a mesh** (a.k.a. The mesh if you would apply every shapekey, modifier etc. to it)
    - not yet properly tested
- **deleting vertices, faces or edges of a mesh**
- **dealing with coordinates**
- **dealing with keyframes (actions, fcurves)**
- **dealing with vertex groups** 
- **dealing with shape keys**
- **dealing with modifiers**
- some minor functions that help in testing

- more might follow


I try to code these functions and scripts as clean as possible, including:
- proper documentation on how to use them
- great performance (*many functions use foreach_set/foreach_get methods, that are like 10 times faster than normal loops*)
- Almost never using bpy.ops (only if there's no alternative)  

**HOWEVER**, please note:
- I'm constantly adding and changing stuff, which includes renaming or moving functions. This might confuse users in some cases when they try to "update" their functions.


Also, all functions include a 'context' parameter. This is to make proper usage in addon operators more easy.

# source
https://github.com/Cardboy0/toolbox  
(I also have a (decentely big) guide on scripting in Blender, ranging from basis to specific and advanced topics: https://docs.google.com/document/d/1Ph6HpkmEX9KWoPC6V1UVWJ1F37qj9NkIDNQRTP-uSII)


# testing
- if you want to "test" the scripts in this repository - a.k.a. check if they work for you as intended - check out the **doesThisStuffWorkForMe** subfolder (there's another *readme* file inside).
- if you think you can improve a function or class, you can also do the test stuff above to check if your edited code works as intended.

