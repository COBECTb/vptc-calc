"""Native shin mount used by CAD previews (OpenSCAD rotate([180,180,0]))."""

CONNECTOR_TO_SHIN_LINEAR = ((-1, 0, 0), (0, -1, 0), (0, 0, 1))
CONNECTOR_TO_SHIN_TRANSLATION = (-47, 0, 0)


def connector_point_to_shin(point):
    """Apply the native mount; the inverse is the same transform."""
    return tuple(
        sum(row[j] * point[j] for j in range(3)) + offset
        for row, offset in zip(CONNECTOR_TO_SHIN_LINEAR, CONNECTOR_TO_SHIN_TRANSLATION)
    )
