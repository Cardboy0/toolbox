# ##### BEGIN GPL LICENSE BLOCK #####
#
# Part of the "toolbox" repository
# Copyright (C) 2022  Cardboy0 (https://twitter.com/cardboy0)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy


# deals with all (or most) things keyframes (-> fcurves)

def get_or_create_action(something):
    """Get the action of the provided class instance or create a new one if it doesn't exist yet

    This should work on anything that is able to have the animation_data attribute. 

    Parameters
    ----------
    something : anything that can have a animation_data attribute
        The "object" for which you want to get the action

    Returns
    -------
    bpy.types.Action
        found or created action

    Raises
    ------
    Exception
        When something went wrong
    """
    # based on these two posts:
    # https://blender.stackexchange.com/questions/234463/scripting-f-curves
    # https://blender.stackexchange.com/questions/41484/how-do-i-change-actions-in-python

    try:
        if something.animation_data == None:
            something.animation_data_create()
        if hasattr(something.animation_data, 'action') == False or something.animation_data.action == None:
            # create new action
            new_action = bpy.data.actions.new("custom created action")
            something.animation_data.action = new_action
            # this feels dirty, but I don't have a better alternative
        return something.animation_data.action
    except:
        raise Exception(
            "Something went wrong when trying to get the action of " + something.__str__())


def create_key_frames_fast(fcurve, values):
    """If you want to create keyframes for a fcurve in a fast way.

    Attention: Should not be used to add keyframes to an fcurve if any keyframes already exist.

    Parameters
    ----------
    fcurve : bpy.types.FCurve
        The fcurve for which you want keyframes to be created.
        fcurves are part of actions (bpy.types.Action)
    values : list or dictionary
        If list: [frame1,value1, frame2,value2, ...] \n
        If dict: {frame1: value1, frame2: value2, ...} \n
        Using a list is faster than using a dictionary
    """

    # based on https://blender.stackexchange.com/questions/92287/editing-fcurve-keyframe-points-in-fast-mode

    if type(values) == dict:
        x = []
        for key, value in values.items():
            x.extend([key, value])
        values = x

    fcurve.keyframe_points.add(count=len(values) // 2) # two forward slashes because count mustn't be a float
    fcurve.keyframe_points.foreach_set("co", values)
    fcurve.update()
