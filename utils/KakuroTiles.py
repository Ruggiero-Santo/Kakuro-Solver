from functools import reduce

class KakuroTile:
    """The superclass for entries in a Kakuro board."""
    pass


class Blank(KakuroTile):
    """A blank square to be filled in."""
    id = 0

    def __init__(self, value = None, specificId = None):
        if value == None:
            self.possibleValues = [*range(1,10)]
        elif isinstance(value, list):
            self.possibleValues = value
        else:
            self.possibleValues = [value]

        # Give every blank an index for easy identification and to determine
        # if one blank is a copy of another.
        if specificId == None:
            self._id = Blank.id
            Blank.id += 1
        else:
            self._id = specificId

        # Keep track of the sums containing this blank.
        self.sums = []

    def __str__(self):
        """Return a string identifying this blank and possibile value."""
        return 'T%2s->%s' % (self._id, str(self.possibleValues))

    def __repr__(self):
        "     "
        "  @1 "
        """Standard output called from print function. Return srt(value) in 3 char"""
        if len(self.possibleValues) != 1: return "  @"+str(len(self.possibleValues))+" "
        return "  "+str(self.possibleValues[0])+"  "

    def _setValue(self, value):
        """Set the value for this entry. This triggers a reaction where we
        modify the configuration's sums containing this entry and modify them
        accordingly."""
        if value in self.possibleValues:
            self.possibleValues = [value]
        else:
            raise ValueError("Not valid value")

    def recordSum(self, s):
        """Record this entry as appearing in the specified Sum object."""
        if s not in self.sums:
            self.sums.append(s)

    @DeprecationWarning
    def filterSumFromValue(self):
        """Iterate over all the sums containing this blank, and filter out
        all of the configurations over those sums that contain an invalid
        entry for this blank."""

        changed = False
        for sum in self.sums:
            changed |= sum.filterConfigFromTile(self)

        return changed# Report if anything changed.

    def filterValuesFromSums(self):
        """This entry can only have certain values in each sum it appears in.
        The possible values that it can have overall is the intersection of
        its current possible values with the possible values in each of the
        sums in which it appears."""
        
        newPossibleValues = list(reduce(lambda x,y: x.intersection(y),
                                [set(sum.getValuesForTile(self)) for sum in self.sums],
                                set(self.possibleValues)))
        changed = (newPossibleValues != self.possibleValues)
        self.possibleValues = newPossibleValues

        return changed # Report if anything changed.

    def deepcopy(self):
        copy = Blank(value = self.possibleValues[:], specificId = self._id)
        #Sum is not copied because will registered during copy of sum
        return copy

class Brick(KakuroTile):
    """A brick, not editable, i.e. solid space."""

    def __init__(self, v=None, h=None):
        self.verticalSum = v
        self.horizontalSum = h

    def __str__(self):
        mid = " sum of "
        res = ""
        if self.verticalSum:
            res += "vertical" + mid + self.verticalSum+","
        if self.horizontalSum:
            res += "horizontal" + mid + self.horizontalSum

    def __repr__(self):
        c = "#"
        res = str(self.verticalSum if self.verticalSum else c).ljust(2, c) + c
        res += str(self.horizontalSum if self.horizontalSum else c).ljust(2, c)
        return res

    def deepcopy(self):
        return Brick(self.verticalSum, self.horizontalSum)
