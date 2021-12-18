import bpy

D = bpy.data


# for dealing with collections in general (but not viewlayer collections)


def linkObjectToCollections(context,obj, collections):
    """"Clean" linking of an object into one or multiple collections, i.e. unlinking it from any other collections at the same time.

    Parameters
    ----------
    obj : bpy.types.Object
        Object to link
    collections : bpy.types.Collection or list
        Collection(s) to link into. Know that the main collection of a scene is kinda special and located at Scene.collection
    """
    # careful: Unlinking an object from all collections of the current scene makes it "disappear" and inactive.
    # As such it's best to always have it linked to at least one collection in the current scene.
    collectionsToDelete = list(obj.users_collection)
    if isinstance(collections, list) == False:
        collections = [collections]
    # link
    for coll in collections:
        if coll.objects.find(obj.name) == -1:
            coll.objects.link(obj)
        else:
            # trying to link an object to a collection it's already linked to gives an error.
            continue
    # unlink
    # using the 'in' operator with a set is magnitudes faster than with a list.
    collections = set(collections)
    for coll in collectionsToDelete:
        if coll not in collections:
            coll.objects.unlink(obj)


def linkCollectionToCollections(context,coll, collections):
    """ "Clean" linking of a collection into one or multiple other collections, i.e. unlinking it from any other collections at the same time.

    Parameters
    ----------
    coll : bpy.types.Collection
        Collection you want to link
    collections : bpy.types.Collection or list
        Collection(s) to link into. Know that the main collection of a scene is kinda special and located at Scene.collection
    onlyScene : bool, optional
        Whether you want to unlink the collection from only parent collections in the current scene, or in the whole file. Might impact performance., by default True
    """
    # Same as with linkObjectToCollections(), we should make sure that the collection never gets completely unlinked from its current scene (if it was linked in the first place).

    if isinstance(collections, list) == False:
        collections = set([collections])
    else:
        collections = set(collections)
    # Unlike objects, collections don't have a .users_collection property. This means we will have to do some searching.

    # important: D.collections doesn't have ALL the collections, the master collections of each scene are not included and thus must be added manually
    allCollections = set(D.collections)
    for scene in D.scenes:
        allCollections.add(scene.collection)  # adding the master collections

    # search for parent collections so we can unlink them later
    # this is a simple number, not a list or something similar
    remainingNumberOfUsers = coll.users
    deleteCollections = []
    for testCollection in allCollections:
        if remainingNumberOfUsers == 0:
            break  # if we know that our collection has 3 users, we only need to search through all collections until we got 3 matches
        if testCollection.children.find(coll.name) != -1:
            remainingNumberOfUsers -= 1
            deleteCollections.append(testCollection)

    for linkCollection in collections:
        # if it's already linked to this collection an error would appear
        if linkCollection.children.find(coll.name) == -1:
            linkCollection.children.link(coll)

    # using the 'in' operator with a set is magnitudes faster than with a list.
    for parent in deleteCollections:
        if parent not in collections:
            parent.children.unlink(coll)


def createCollection(context,name, parentCollection="MASTER", avoidDuplicates=False):
    """Create a new collection inside a specific parent collection.

    Know that same as with objects, no two collections can have the same name and as such your chosen name may not be the actual one of this new collection.


    Parameters
    ----------
    name : str
        The name of the collection to create
    parentCollection : bpy.types.Collection or "MASTER", optional
        The collection in which you want to create the new collection., by default "MASTER" (uses the main collection of the current scene).
    avoidDuplicates : bool, optional
        If True and a collection with the EXACT same name already exists in the parent collection, no new collection will be created. Does NOT check in any other collections., by default False

    Returns
    -------
    bpy.types.Collection
        The newly created collection (or if avoidDuplicates==True and an already existing collection was found, this collection)
    """
    if parentCollection == "MASTER":
        parentCollection = context.scene.collection
    if avoidDuplicates == True:
        index = parentCollection.children.find(name)
        if index != -1:
            return parentCollection.children[index]

    newCollection = D.collections.new(name=name)
    parentCollection.children.link(newCollection)
    return newCollection
