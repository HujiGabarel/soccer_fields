import numpy as np
def square(width, dtype=np.uint8, *, decomposition=None):
    """Generates a flat, square-shaped footprint.
    Every pixel along the perimeter has a chessboard distance
    no greater than radius (radius=floor(width/2)) pixels.
    Parameters
    ----------
    width : int
        The width and height of the square.
    Other Parameters
    ----------------
    dtype : data-type, optional
        The data type of the footprint.
    decomposition : {None, 'separable', 'sequence'}, optional
        If None, a single array is returned. For 'sequence', a tuple of smaller
        footprints is returned. Applying this series of smaller footprints will
        given an identical result to a single, larger footprint, but often with
        better computational performance. See Notes for more details.
        With 'separable', this function uses separable 1D footprints for each
        axis. Whether 'seqeunce' or 'separable' is computationally faster may
        be architecture-dependent.
    Returns
    -------
    footprint : ndarray or tuple
        The footprint where elements of the neighborhood are 1 and 0 otherwise.
        When `decomposition` is None, this is just a numpy.ndarray. Otherwise,
        this will be a tuple whose length is equal to the number of unique
        structuring elements to apply (see Notes for more detail)
    Notes
    -----
    When `decomposition` is not None, each element of the `footprint`
    tuple is a 2-tuple of the form ``(ndarray, num_iter)`` that specifies a
    footprint array and the number of iterations it is to be applied.
    For binary morphology, using ``decomposition='sequence'`` or
    ``decomposition='separable'`` were observed to give better performance than
    ``decomposition=None``, with the magnitude of the performance increase
    rapidly increasing with footprint size. For grayscale morphology with
    square footprints, it is recommended to use ``decomposition=None`` since
    the internal SciPy functions that are called already have a fast
    implementation based on separable 1D sliding windows.
    The 'sequence' decomposition mode only supports odd valued `width`. If
    `width` is even, the sequence used will be identical to the 'separable'
    mode.
    """
    if decomposition is None:
        return np.ones((width, width), dtype=dtype)

    if decomposition == 'separable' or width % 2 == 0:
        sequence = [(np.ones((width, 1), dtype=dtype), 1),
                    (np.ones((1, width), dtype=dtype), 1)]
    elif decomposition == 'sequence':
        # only handles odd widths
        sequence = [(np.ones((3, 3), dtype=dtype), _decompose_size(width, 3))]
    else:
        raise ValueError(f"Unrecognized decomposition: {decomposition}")
    return tuple(sequence)

def _decompose_size(size, kernel_size=3):
    """Determine number of repeated iterations for a `kernel_size` kernel.
    Returns how many repeated morphology operations with an element of size
    `kernel_size` is equivalent to a morphology with a single kernel of size
    `n`.
    """
    if kernel_size % 2 != 1:
        raise ValueError("only odd length kernel_size is supported")
    return 1 + (size - kernel_size) // (kernel_size - 1)