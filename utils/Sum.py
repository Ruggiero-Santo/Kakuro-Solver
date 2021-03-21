from functools import reduce

class Sum:
    """Represents a sum in the board, i.e. the value of the sum and the iist of
    Blank objects contributing to that sum."""

    def __init__(self, value, tileList, isCopy=False):
        self.value = value
        self.tileList = tileList

        # If this is not a copying operation, we calculate all possible assignments.
        if not(isCopy):
            self.configurations = list(Sum._findConfiguration(self.value, self.tileList))

        # Record each entry as appearing in this sum.
        for tile in tileList:
            tile.recordSum(self)

        #indicating that the sum is not yet fully determined.
        self._isComplete = False

    def __str__(self):
        res = str(self.value) + " -> " + str([str(tile) for tile in self.tileList])
        for conf in self.configurations:
            res += "\n\t" + str(conf)
        return res
    
    @staticmethod
    def _findConfiguration(value, tileList, exclude = []):
        """_findConfiguration(value, tileList, exclude=[])

        Given a value that will be excluded, find all possible assignments of values
        to entries that satisfies this value. Exclude can be used to exclude certain
        possible values. In this case, it is used recursively to make sure that each
        possible number appears at most once in each sum."""

        if value == 0 and len(tileList) == 0:
            yield []# If we have a full sum, yield it.

        if len(tileList) == 0:
            return# If we are out of tiles to fill, we failed.

        valid_tileList = [list(filter(lambda x: x not in exclude, tile.possibleValues)) for tile in tileList]
        if not reduce(lambda x,y: x and y, valid_tileList , True):
            return # If we have no possible value left for any remaining position, we failed.

        if sum([max(valid_tile) for valid_tile in valid_tileList]) < value:
            return # If we cannot even use the biggest guys to complete, stop.

        if sum([min(valid_tile) for valid_tile in valid_tileList]) > value:
            return# If we cannot even use the smallest guys to complete, stop.

        # Otherwise, try to fill in the next position and reiterate.
        for candidate in valid_tileList[0]:
            for s in Sum._findConfiguration(value - candidate, tileList[1:], exclude + [candidate]):
                yield [candidate] + s

    def deepcopy(self, memo = None):
        copyTiles = memo
        if memo == None:
            copyTiles = [tile.deepcopy() for tile in self.tileList]
        else:
            copyTiles = [memo[tile._id] for tile in self.tileList]

        copy = Sum(self.value, copyTiles, isCopy = True)
        copy.configurations = self.configurations[:]
        return copy

    @DeprecationWarning
    def isComplete(self):
        """Return True if this sum is completely defined and has been processed.
            False otherwise."""
        if self._isComplete:
            return self._isComplete
        elif len(self.configurations) == 1:
            # We only do this once, so mark to indicate this.
            self._isComplete = True
            # Now for every entry in this sum, set it to its value.
            for tile, value in zip(self.tileList, self.configurations[0]):
                tile._setValue(value)

        return self._isComplete

    def filterConfigFromTile(self, tile):
        """For a given tile, filter out all configurations that are not valid
        based on the possible values for the entry."""


        idx = self.tileList.index(tile)# Get the index in configurations for tile.

        # Filter, allowing only possible entries for entry.
        newConfigurations = list(filter(lambda x: x[idx] in tile.possibleValues, self.configurations))
        changed = (newConfigurations != self.configurations)
        self.configurations = newConfigurations

        # Report if anything changed.
        return changed

    def getValuesForTile(self, tile):
        """Given an tile appearing in the sum, determine all the possible values it can
            have in the sum."""

        # Get the index in the configurations for the tile.
        i = self.tileList.index(tile)
        # Find all possible values for tile over the configurations.
        return [config[i] for config in self.configurations]