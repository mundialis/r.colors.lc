## DESCRIPTION

*r.colors.lc* sets the colors for a land cover classification.

There are different variants of how the color values can be selected.

The first one is that a reference vector map **referencemap** with a
class column **class_column** and a r:g:b color column **color_column**
is passed as parameter. Then the color values from the color column are
set for the corresponding classes. If the class information in the class
column contains integer values, these are assigned directly to the map
values. If the values are string values, the category label of the map
is used.

The second possibility is to pass only a land cover map **map**. If this
map has a category label, it is tried to match it with fuuzy logic to a
land cover class color dictionary and set the colors automatically. If
the map does not have category labels, a random color map is added.

## EXAMPLES

### Assign color from color column in referencemap

```sh
r.colors.lc referencemap=incora_dortmund_LULC_training_points_color map=classification color_column=color class_column=lulc_int
```

### Matching land cover category labels with fuzzy logic

```sh
r.colors.lc map=classification
```

## SEE ALSO

*[r.colors.fuzzy_lc](r.colors.fuzzy_lc.md) (addon),
[v.colors.to.rast](v.colors.to.rast.md) (addon)*

## AUTHORS

Anika Weinmann and Guido Riembauer,
[mundialis](https://www.mundialis.de/), Germany
