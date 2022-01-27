#!/usr/bin/env python3

############################################################################
#
# MODULE:       r.colors.lc
#
# AUTHOR(S):    Anika Betttge and Guido Riembauer
#
# PURPOSE:      Sets the colors for a land cover classification
#
# COPYRIGHT:    (C) 2020-2022 by mundialis GmbH & Co. KG and the GRASS Development Team
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#############################################################################

# %Module
# % description: Sets the colors for a land cover classification.
# % keyword: raster
# % keyword: colors
# % keyword: land cover
# % keyword: fuzzy logic
# % keyword: Levenshtein Distance
# %end

# %option G_OPT_R_INPUT
# % key: map
# % required: yes
# % label: Name of input land cover map
# %end

# %option G_OPT_V_INTPUT
# % key: referencemap
# % required: no
# % label: Name for input vector map
# % description: Needs a column with class information. If a color column is given these colors are written to the raster
# %end

# %option G_OPT_DB_COLUMN
# % key: color_column
# % required: no
# % label: Name of color column in referencemap
# % description: Color have to be given in format like r:g:b e.g. 255:255:255
# %end

# %option G_OPT_DB_COLUMN
# % key: class_column
# % required: no
# % label: Name of class information column in referencemap
# % description: Takes class information as string or integer. If color_column is not given and type is int random colors are set, otherwise Levenshtein Distance is used to match colors
# %end

# %rules
# % collective: referencemap,class_column,color_column
# %end


import grass.script as grass
from random import randrange


def main():

    # parameters
    referencemap = options["referencemap"]
    map = options["map"]
    color_column = options["color_column"]
    class_column = options["class_column"]

    # test if necessary GRASS GIS addons are installed
    if not grass.find_program("v.colors.to.rast", "--help"):
        grass.fatal(
            _(
                "The 'v.colors.to.rast' module was not found, install it first:"
                + "\n"
                + "g.extension r.colors.fuzzy_lc url=..."
            )
        )
    if not grass.find_program("r.colors.fuzzy_lc", "--help"):
        grass.fatal(
            _(
                "The 'r.colors.fuzzy_lc' module was not found, install it first:"
                + "\n"
                + "g.extension r.colors.fuzzy_lc url=..."
            )
        )

    map_class_labels = list(
        grass.parse_command("r.category", map=map, separator="tab").keys()
    )
    has_cat_label = True
    for label in map_class_labels:
        if "\t" not in label:
            has_cat_label = False

    if color_column:
        grass.message(_("Using colors from column <%s>...") % color_column)
        grass.run_command(
            "v.colors.to.rast",
            referencemap=referencemap,
            map=map,
            color_column=color_column,
            class_column=class_column,
        )
    elif has_cat_label:
        grass.message(_("Matching land cover classes..."))
        grass.run_command("r.colors.fuzzy_lc", map=map)
    else:
        grass.warning(
            _("Input map has missing category labels. Setting random colors...")
        )
        # TODO remove workaround with own random colors and use only r.colors
        # because of the r.colors.out issue:  https://github.com/OSGeo/grass/issues/878
        # grass.run_command('r.colors', map=map, color='random')
        random_colors = []
        colors_to_generate = 40
        for i in range(colors_to_generate):
            random_colors.append(
                "{}:{}:{}".format(randrange(255), randrange(255), randrange(255))
            )

        cellstats = grass.read_command(
            "r.stats", input=map, separator="pipe", flags="cn"
        )
        cellvals = [line.split("|")[0] for line in cellstats.splitlines()]
        # modify the color table:
        if len(cellvals) > len(random_colors):
            grass.run_command("r.colors", map=map, color="random")
            grass.warning(
                _(
                    "More cells values than %d: using r.colors color=random; r.colors.out_sld does not work correctly"
                )
                % len(random_colors)
            )
        colors_str = [
            "%s %s" % (val, color)
            for val, color in zip(cellvals, random_colors[: len(cellvals)])
        ]
        bc = grass.feed_command("r.colors", quiet=True, map=map, rules="-")
        bc.stdin.write(grass.encode("\n".join(colors_str)))
        bc.stdin.close()
        bc.wait()

        # set category labels to raster values if raster type is CELL
        mapinfo = grass.raster_info(map)
        if mapinfo["datatype"] == "CELL":
            cellstats = grass.read_command(
                "r.stats", input=map, separator="pipe", flags="cn"
            )
            category_text = ""
            for line in cellstats.splitlines():
                val = line.split("|")[0]
                category_text += "%s|%s\n" % (val, val)
            # assign labels
            cat_proc = grass.feed_command(
                "r.category", map=map, rules="-", separator="pipe"
            )
            cat_proc.stdin.write(category_text.encode())
            cat_proc.stdin.close()
            # feed_command does not wait until finished
            cat_proc.wait()


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
