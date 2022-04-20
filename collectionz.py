import bpy

# for dealing with collections in general (but not viewlayer collections)
#
# You may ask yourself "why name it 'collectionz.py' with a z?"
# Because due to some very weird reasons, calling it 'collections.py' results in my VS code
# not being able to format code anymore, INCLUDING other files. It just disables it, I don't know why.


def link_object_to_collections(obj, collections, keep_links=False):
    """Links an object into one or multiple collections. By default also unlinks the obj from any other collections it's already in.

    Parameters
    ----------
    obj : bpy.types.Object
        Object to link
    collections : bpy.types.Collection or list
        Collection(s) to link into. Know that the main collection of a scene is kinda special and located at Scene.collection
    keep_links : bool
        If True, the function will not unlink the obj from any collections it's already in.
    """
    if isinstance(collections, list) == False:
        collections = [collections]

    # careful: Unlinking an object from all collections of the current scene makes it "disappear" and inactive.
    # As such it's best to always have it linked to at least one collection in the current scene.
    if keep_links == False:
        collections_to_delete = list(obj.users_collection)

    # link
    for coll in collections:
        if coll.objects.find(obj.name) == -1:
            coll.objects.link(obj)
        else:
            # trying to link an object to a collection it's already linked to gives an error.
            continue

    if keep_links == False:
        # unlink
        # using the 'in' operator with a set is magnitudes faster than with a list.
        collections = set(collections)
        for coll in collections_to_delete:
            if coll not in collections:
                coll.objects.unlink(obj)


def link_collection_to_collections(coll, collections, keep_links=False):
    """ "Clean" linking of a collection into one or multiple other collections, i.e. unlinking it from any other collections at the same time.

    Parameters
    ----------
    coll : bpy.types.Collection
        Collection you want to link
    collections : bpy.types.Collection or list
        Collection(s) to link into. Know that the main collection of a scene is kinda special and located at Scene.collection
    keep_links : bool
        If True, the function will not unlink the collection from any collections it's already in.
    """
    # Same as with linkObjectToCollections(), we should make sure that the collection never gets completely unlinked from its current scene (if it was linked in the first place).

    if isinstance(collections, list) == False:
        collections = set([collections])
    else:
        collections = set(collections)

    if keep_links == False:
        # Unlike objects, collections don't have a .users_collection property. This means we will have to do some searching.

        # important: D.collections doesn't have ALL the collections, the master collections of each scene are not included and thus must be added manually
        all_collections = set(bpy.data.collections)
        for scene in bpy.data.scenes:
            # adding the master collections
            all_collections.add(scene.collection)

        # search for parent collections so we can unlink them later
        # this is a simple number, not a list or something similar
        remaining_number_of_users = coll.users
        delete_collections = []
        for test_collection in all_collections:
            if remaining_number_of_users == 0:
                break  # if we know that our collection has 3 users, we only need to search through all collections until we got 3 matches
            if test_collection.children.find(coll.name) != -1:
                remaining_number_of_users -= 1
                delete_collections.append(test_collection)

    for link_collection in collections:
        # if it's already linked to this collection an error would appear
        if link_collection.children.find(coll.name) == -1:
            link_collection.children.link(coll)

    if keep_links == False:
        # using the 'in' operator with a set is magnitudes faster than with a list.
        for parent in delete_collections:
            if parent not in collections:
                parent.children.unlink(coll)


def create_collection(context, name, parent_collection="MASTER", avoid_duplicates=False):
    """Create a new collection inside a specific parent collection.

    Know that same as with objects, no two collections can have the same name and as such your chosen name may not be the actual one of this new collection.


    Parameters
    ----------
    name : str
        The name of the collection to create
    parent_collection : bpy.types.Collection or "MASTER", optional
        The collection in which you want to create the new collection., by default "MASTER" (uses the main collection of the current scene).
    avoid_duplicates : bool, optional
        If True and a collection with the EXACT same name already exists in the parent collection, no new collection will be created. Does NOT check in any other collections., by default False

    Returns
    -------
    bpy.types.Collection
        The newly created collection (or if avoidDuplicates==True and an already existing collection was found, this collection)
    """
    if parent_collection == "MASTER":
        parent_collection = context.scene.collection
    if avoid_duplicates == True:
        index = parent_collection.children.find(name)
        if index != -1:
            return parent_collection.children[index]

    new_collection = bpy.data.collections.new(name=name)
    parent_collection.children.link(new_collection)
    return new_collection
