from utils.KakuroTiles import Brick, Blank
from utils.Sum import Sum

class KakuroBoard:
    """A Kakuro board is represented by a two dimensional array with Tile of
    type KakuroTile representing the data at position x,y."""

    def __init__(self, board, tiles = []):

        def createSum(value, tiles):
            blocks = []
            for tile in tiles:
                if isinstance(tile, Brick):
                    break
                blocks.append(tile)
            return Sum(value, blocks)

        if isinstance(board, str):
            board = KakuroBoard._parse(board)

        self.board = board
        self.tiles = tiles
        self.sums = []

        # Convert to internal data structure, namely a list of sums represented
        # in the following way:
        # sum, [Blanks in the sum]
        sums = []
        if self.tiles == []:
            for x, row in enumerate(board):
                for y, tile in enumerate(row):
                    # If the tile is a sum, process the sum.
                    if isinstance(tile, Brick):
                        if tile.verticalSum:
                            col = [board[i][y] for i in range(x+1, len(board))]
                            sums.append(createSum(tile.verticalSum, col))
                        if tile.horizontalSum:
                            sums.append(createSum(tile.horizontalSum, row[y+1:]))

                    elif isinstance(tile, Blank):
                        self.tiles.append(tile)

        # We have the structure.
        self.sums = sums

    def __repr__(self):
        res = ""
        pr = lambda x: x if isinstance(x, Brick) else self.tiles[x._id]
        for row in self.board:
            res += str([pr(tile) for tile in row]) + "\n"
        return res

    def __str__(self):
        res = ""
        for row in self.board:
            res += str([tile for tile in row]) + "\n"
        return res

    def deepcopy(self):
        """Given a board, make a copy of it."""
        copyBoard = [[tile.deepcopy() for tile in row] for row in self.board]
        return KakuroBoard(copyBoard)

    def solve(self):
        """Solve the board."""
        # Making a copy, since we don't want to change the actual
        # Blank tiles themselves through computation. Thus, they are preserved
        # and this class represents a fresh, clean sheet of paper with no
        # writing on it at all times.

        # Now we use the auxiliary method on the data structure copy until all
        # the tiles are solved.
        return self._solve(*KakuroBoard._mycopy(self.tiles, self.sums))

    def _solve(self, tiles, sums, add = []):

        def arc_reduce(arc):
            """Revision face that recompute domain of node according constraint"""
            # instead to compute every single time the new domain according all
            # node involved in the hyper-node, all valid configurations are
            # pre-computed and deleted invalideted configurations according
            # domains modify
            return arc[0].filterValuesFromSums() or arc[1].filterConfigFromTile(arc[0])

        #--------Node Consistency
        for x in tiles:
            x.filterValuesFromSums() 

        #---------GAC (General Arc Consistency or hyper-arc consistency)
        # make a list of hyper-node that must be computed

        # procedure GAC( <Vs, dom, Cs> )
        #     to_do = { <X, c> ∣ c ∈ Cs and X ∈ scope(c) }
        #     while to_do ≠ {} do
        #         select and remove <X, c> from to_do
        #         let { Y1, …, Yk } = scope(c) ∖ {X}
        #         ND := { x ∣ x ∈ dom [X] and exists y1 ∈ dom [ Y1 ] … y k ∈ dom [Yk] such that c ( X = x, Y1 = y1, …, Yk = yk) }
        #         if ND ≠ dom [ X ] then
        #             to_do := to_do ∪ { <Z, c′> ∣ { X, Z } ⊆ scope(c′) , c′≠c, Z≠X }
        #             dom[X]:=ND
        #         return dom

        worklist = set()
        for x in tiles:
            # if len(x.possibleValues) > 1:
            for c in x.sums:
                worklist.add((x, c))

        # compute all elements in worklist list
        while not len(worklist) == 0:
            # remove one hyper-node
            arc = worklist.pop()
            if arc_reduce(arc):
                if len(arc[0].possibleValues) == 0:
                    return False
                else:
                    for c in arc[0].sums:
                        for x in c.tileList:
                            worklist.add((x, c))
        #---------Backtrack
        if all([len(sum.configurations) > 1 for sum in sums]):
            return False
        # If the board is complete, we are done.
        if all([len(tile.possibleValues) == 1 for tile in tiles]):
            yield tiles
        else: # If any tiles are empty, we must backtrack.
            # Things are now stable, so we must branch on a possible value.
            branchingTiles = sorted([(len(tile.possibleValues), tile._id)
                                    for tile in tiles if len(tile.possibleValues) > 1])
            # Pick the tile with the fewest choices to minimize branching.
            tileID = branchingTiles[0][1]

            # Try all possible values for this tile.
            for value in tiles[tileID].possibleValues:
                # Create a copy of the board.
                cTiles, cSums = KakuroBoard._mycopy(tiles, sums)
                cTiles[tileID]._setValue(value)

                # Iteratively solve.
                for solution in self._solve(cTiles, cSums):
                    yield solution

    @staticmethod
    def _mycopy(tiles, sums):
        """Given a board, make a copy of it. This is used in backtracking.

        NOTE: We are not making a full copy of this object so much as we are
        simply copying the tiles and sums lists."""


        # The tiles are specifically going to be what changes, so begin by
        # copying them.
        cTiles = [tile.deepcopy() for tile in tiles]

        # Now copy the sums. Note that doing so automatically will register each
        # of the tiles with the appropriate sums as required.
        cSums = [sum.deepcopy(cTiles) for sum in sums]

        return cTiles, cSums

    @staticmethod
    def _parse(filename):

        def parse_row(row):
            parsed_row = []
            for item in row:

                if item == "#":
                    parsed_row.append(Brick())

                elif item == "":
                    parsed_row.append(Blank())

                else:
                    item = item.split("-")

                    v, h = None, None
                    try:
                        v = int(item[0])
                    except ValueError:
                        pass

                    try:
                        h = int(item[1])
                    except ValueError:
                        pass

                    parsed_row.append(Brick(v=v, h=h))

            return parsed_row

        import csv
        with open(filename, encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            board = []

            for row in csv_reader:
                board.append(parse_row(row))

        return board
        


if __name__ == '__main__':
    # EXAMPLE 7x7
    # board = [[Brick(),    Brick(v=5),       Brick(v=23), Brick(v=6), Brick(v=30), Brick(),     Brick()],
    #         [Brick(h=12), Blank(),          Blank(),     Blank(),    Blank(3),    Brick(v=15), Brick(v=5)],
    #         [Brick(h=27), Blank(),          Blank(),     Blank(),    Blank(),     Blank(),     Blank()],
    #         [Brick(),     Brick(v=24,h=31), Blank(),     Blank(),    Blank(),     Blank(),     Blank()],
    #         [Brick(),     Blank(),          Brick(v=15), Brick(v=4), Blank() ,    Brick(v=3),  Brick(v=17)],
    #         [Brick(h=34), Blank(8),         Blank(),     Blank(),    Blank(),     Blank(),     Blank()],
    #         [Brick(h=32), Blank(),          Blank(),     Blank(),    Blank(),     Blank(),     Blank()]]
    # EXAMPLE 7x7
    # board = [[Brick(),     Brick(v=18),    Brick(v=8),     Brick(),        Brick(),        Brick(v=17),Brick(v=13)],
    #         [Brick(h=21), Blank(),        Blank(),        Blank(),        Brick(v=22,h=14),Blank(),   Blank()],
    #         [Brick(h=3),  Blank(),        Blank(),        Brick(v=23,h=21),Blank(),       Blank(),    Blank()],
    #         [Brick(h=27), Blank(),        Blank(3),       Blank(),        Blank(),        Brick(v=8), Brick(v=24)],
    #         [Brick(),     Brick(v=16),    Brick(v=4,h=24),Blank(),        Blank(),        Blank(),    Blank(8)],
    #         [Brick(h=20), Blank(),        Blank(),        Blank(8),       Brick(h=14),    Blank(),    Blank()],
    #         [Brick(h=8),  Blank(),        Blank(),        Brick(h=17),    Blank(),        Blank(),    Blank()]]
    # EXAMPLE 10 x 10
    # board = [[Brick(), Brick(v=14), Brick(v=5), Brick(v=28), Brick(v=3), Brick(), Brick(), Brick(v=26), Brick(v=5), Brick(v=22)],
    #          [Brick(h=12), Blank(), Blank(), Blank(), Blank(), Brick(v=12,h=24), Blank(), Blank(), Blank(), Blank()],
    #          [Brick(h=23), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(v=32,h=21), Blank(), Blank(), Blank()],
    #          [Brick(), Brick(v=7), Brick(v=39), Blank(), Brick(h=6), Blank(), Blank(), Blank(), Brick(v=24), Blank()],
    #          [Brick(h=20), Blank(), Blank(), Blank(), Brick(v=19,h=27), Blank(), Blank(), Blank(), Blank(), Brick(v=34)],
    #          [Brick(h=6), Blank(), Blank(), Brick(v=22,h=23), Blank(), Blank(), Blank(), Brick(v=13,h=15), Blank(), Blank()],
    #          [Brick(h=14), Blank(), Blank(), Blank(), Blank(), Brick(h=14), Blank(), Blank(), Blank(), Blank()],
    #          [Brick(), Brick(v=6,h=22), Blank(), Blank(), Blank(), Brick(v=4,h=16), Blank(), Blank(), Brick(v=17), Blank()],
    #          [Brick(h=21), Blank(), Blank(), Blank(), Brick(h=24), Blank(), Blank(), Blank(), Blank(), Blank()],
    #          [Brick(h=15), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(h=20), Blank(), Blank(), Blank()]]
    # # EXAMPLE 20 x 20
    # board = [
    #     [Brick(), Brick(), Brick(), Brick(v=28), Brick(v=17), Brick(v=3), Brick(), Brick(), Brick(v=30), Brick(v=19), Brick(), Brick(), Brick(), Brick(), Brick(v=24), Brick(v=23), Brick(), Brick(), Brick(), Brick()],
    #     [Brick(), Brick(), Brick(h=16), Blank(), Blank(), Blank(), Brick(), Brick(h=16), Blank(), Blank(), Brick(), Brick(), Brick(), Brick(v=3, h=15), Blank(), Blank(), Brick(), Brick(), Brick(), Brick()],
    #     [Brick(), Brick(v=23), Brick(v=21, h=19), Blank(), Blank(), Blank(), Brick(), Brick(h=8), Blank(), Blank(), Brick(), Brick(), Brick(h=19), Blank(), Blank(), Blank(), Brick(v=28), Brick(v=7), Brick(v=16), Brick()],
    #     [Brick(h=14), Blank(), Blank(), Blank(), Brick(v=3), Brick(v=17), Brick(), Brick(v=23, h=17), Blank(), Blank(), Brick(), Brick(), Brick(h=32), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Brick()],
    #     [Brick(h=29), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(v=11, h=17), Blank(), Blank(), Brick(), Brick(v=17), Brick(v=11), Brick(v=29), Brick(), Brick(), Brick(h=20), Blank(), Blank(), Blank(), Brick()],
    #     [Brick(h=15), Blank(), Blank(), Brick(v=16, h=20), Blank(), Blank(), Blank(), Blank(), Brick(v=34), Brick(v=6, h=19), Blank(), Blank(), Blank(), Brick(), Brick(), Brick(v=4, h=7), Blank(), Blank(), Brick(), Brick()],
    #     [Brick(), Brick(v=4, h=10), Blank(), Blank(), Brick(), Brick(v=7, h=32), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(), Brick(v=7, h=11), Blank(), Blank(), Brick(v=16), Brick(v=17), Brick()],
    #     [Brick(h=11), Blank(), Blank(), Blank(), Brick(h=7), Blank(), Blank(), Brick(h=12), Blank(), Blank(), Brick(h=13), Blank(), Blank(), Brick(v=30, h=5), Blank(), Blank(), Brick(v=10, h=11), Blank(), Blank(), Brick()],
    #     [Brick(h=8), Blank(), Blank(), Brick(v=35), Brick(v=11, h=4), Blank(), Blank(), Brick(v=19, h=9), Blank(), Blank(), Brick(h=15), Blank(), Blank(), Blank(), Blank(), Brick(h=13), Blank(), Blank(), Blank(), Brick()],
    #     [Brick(), Brick(), Brick(h=10), Blank(), Blank(), Blank(), Brick(h=13), Blank(), Blank(), Brick(), Brick(), Brick(), Brick(v=15, h=10), Blank(), Blank(), Brick(h=6), Blank(), Blank(), Brick(), Brick()],
    #     [Brick(), Brick(), Brick(h=12), Blank(), Blank(), Brick(), Brick(v=23, h=16), Blank(), Blank(), Brick(), Brick(), Brick(h=7), Blank(), Blank(), Brick(), Brick(v=24, h=10), Blank(), Blank(), Brick(), Brick()],
    #     [Brick(), Brick(), Brick(v=16, h=9), Blank(), Blank(), Brick(h=8), Blank(), Blank(), Brick(v=29), Brick(v=11), Brick(), Brick(v=6, h=11), Blank(), Blank(), Brick(v=10, h=10), Blank(), Blank(), Blank(), Brick(v=29), Brick(v=3)],
    #     [Brick(), Brick(h=22), Blank(), Blank(), Blank(), Brick(v=3, h=18), Blank(), Blank(), Blank(), Blank(), Brick(h=3), Blank(), Blank(), Brick(v=12), Blank(), Blank(), Brick(), Brick(v=4, h=9), Blank(), Blank()],
    #     [Brick(), Brick(h=13), Blank(), Blank(), Brick(v=25, h=9), Blank(), Blank(), Brick(h=9), Blank(), Blank(), Brick(v=16, h=8), Blank(), Blank(), Brick(v=23, h=10), Blank(), Blank(), Brick(h=11), Blank(), Blank(), Brick()],
    #     [Brick(), Brick(), Brick(), Brick(v=7, h=10), Blank(), Blank(), Brick(), Brick(h=34), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(v=4), Brick(v=16, h=10), Blank(), Blank(), Brick(v=23)],
    #     [Brick(), Brick(), Brick(v=17, h=9), Blank(), Blank(), Brick(), Brick(), Brick(h=22), Blank(), Blank(), Blank(), Brick(), Brick(v=29, h=21), Blank(), Blank(), Blank(), Blank(), Brick(v=11, h=9), Blank(), Blank()],
    #     [Brick(), Brick(h=18), Blank(), Blank(), Blank(), Brick(v=7), Brick(v=23), Brick(v=3), Brick(), Brick(), Brick(), Brick(v=24, h=15), Blank(), Blank(), Brick(h=21), Blank(), Blank(), Blank(), Blank(), Blank()],
    #     [Brick(), Brick(h=25), Blank(), Blank(), Blank(), Blank(), Blank(), Blank(), Brick(), Brick(), Brick(h=15), Blank(), Blank(), Brick(), Brick(), Brick(v=17), Brick(v=16, h=17), Blank(), Blank(), Blank()],
    #     [Brick(), Brick(), Brick(), Brick(), Brick(h=11), Blank(), Blank(), Blank(), Brick(), Brick(), Brick(h=12), Blank(), Blank(), Brick(), Brick(h=17), Blank(), Blank(), Blank(), Brick(), Brick()],
    #     [Brick(), Brick(), Brick(), Brick(), Brick(h=11), Blank(), Blank(), Brick(), Brick(), Brick(), Brick(h=17), Blank(), Blank(), Brick(), Brick(h=19), Blank(), Blank(), Blank(), Brick(), Brick()]
    # ]
    
    # board = [
    #     [Brick(), Brick(v=21), Brick(v=12), Brick(v=10)],
    #     [Brick(h=23), Blank(), Blank(), Blank()],
    #     [Brick(h=13), Blank(), Blank(), Blank()],
    #     [Brick(h=7), Blank(), Blank(), Blank()],
    # ]

    kakuro_board = KakuroBoard("Kakuro.txt")
    # kakuro_board = KakuroBoard(board)
    print(kakuro_board)

    for i, tiles in enumerate(kakuro_board.solve()):
        print('*** SOLUTION %dth ***' % (i+1))
        print(repr(KakuroBoard(kakuro_board.board, tiles = tiles)))
    print("End")
