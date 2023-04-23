import numpy as np

xyz_from_rgb = np.array([[0.412453, 0.357580, 0.180423],
                         [0.212671, 0.715160, 0.072169],
                         [0.019334, 0.119193, 0.950227]])
@channel_as_last_axis()
def rgb2lab(rgb, illuminant="D65", observer="2", *, channel_axis=-1):
    """Conversion from the sRGB color space (IEC 61966-2-1:1999)
    to the CIE Lab colorspace under the given illuminant and observer.
    Parameters
    ----------
    rgb : (..., 3, ...) array_like
        The image in RGB format. By default, the final dimension denotes
        channels.
    illuminant : {"A", "B", "C", "D50", "D55", "D65", "D75", "E"}, optional
        The name of the illuminant (the function is NOT case sensitive).
    observer : {"2", "10", "R"}, optional
        The aperture angle of the observer.
    channel_axis : int, optional
        This parameter indicates which axis of the array corresponds to
        channels.
        .. versionadded:: 0.19
           ``channel_axis`` was added in 0.19.
    Returns
    -------
    out : (..., 3, ...) ndarray
        The image in Lab format. Same dimensions as input.
    Raises
    ------
    ValueError
        If `rgb` is not at least 2-D with shape (..., 3, ...).
    Notes
    -----
    RGB is a device-dependent color space so, if you use this function, be
    sure that the image you are analyzing has been mapped to the sRGB color
    space.
    This function uses rgb2xyz and xyz2lab.
    By default Observer="2", Illuminant="D65". CIE XYZ tristimulus values
    x_ref=95.047, y_ref=100., z_ref=108.883. See function `get_xyz_coords` for
    a list of supported illuminants.
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Standard_illuminant
    """
    return xyz2lab(rgb2xyz(rgb), illuminant, observer)
@channel_as_last_axis()
def xyz2lab(xyz, illuminant="D65", observer="2", *, channel_axis=-1):
    """XYZ to CIE-LAB color space conversion.
    Parameters
    ----------
    xyz : (..., 3, ...) array_like
        The image in XYZ format. By default, the final dimension denotes
        channels.
    illuminant : {"A", "B", "C", "D50", "D55", "D65", "D75", "E"}, optional
        The name of the illuminant (the function is NOT case sensitive).
    observer : {"2", "10", "R"}, optional
        One of: 2-degree observer, 10-degree observer, or 'R' observer as in
        R function grDevices::convertColor.
    channel_axis : int, optional
        This parameter indicates which axis of the array corresponds to
        channels.
        .. versionadded:: 0.19
           ``channel_axis`` was added in 0.19.
    Returns
    -------
    out : (..., 3, ...) ndarray
        The image in CIE-LAB format. Same dimensions as input.
    Raises
    ------
    ValueError
        If `xyz` is not at least 2-D with shape (..., 3, ...).
    ValueError
        If either the illuminant or the observer angle is unsupported or
        unknown.
    Notes
    -----
    By default Observer="2", Illuminant="D65". CIE XYZ tristimulus values
    x_ref=95.047, y_ref=100., z_ref=108.883. See function `get_xyz_coords` for
    a list of supported illuminants.
    References
    ----------
    .. [1] http://www.easyrgb.com/en/math.php
    .. [2] https://en.wikipedia.org/wiki/CIELAB_color_space
    Examples
    --------

    """
    arr = _prepare_colorarray(xyz, channel_axis=-1)

    xyz_ref_white = get_xyz_coords(illuminant, observer, arr.dtype)

    # scale by CIE XYZ tristimulus values of the reference white point
    arr = arr / xyz_ref_white

    # Nonlinear distortion and linear transformation
    mask = arr > 0.008856
    arr[mask] = np.cbrt(arr[mask])
    arr[~mask] = 7.787 * arr[~mask] + 16. / 116.

    x, y, z = arr[..., 0], arr[..., 1], arr[..., 2]

    # Vector scaling
    L = (116. * y) - 16.
    a = 500.0 * (x - y)
    b = 200.0 * (y - z)

    return np.concatenate([x[..., np.newaxis] for x in [L, a, b]], axis=-1)

@channel_as_last_axis()
def rgb2xyz(rgb, *, channel_axis=-1):
    """RGB to XYZ color space conversion.
    Parameters
    ----------
    rgb : (..., 3, ...) array_like
        The image in RGB format. By default, the final dimension denotes
        channels.
    channel_axis : int, optional
        This parameter indicates which axis of the array corresponds to
        channels.
        .. versionadded:: 0.19
           ``channel_axis`` was added in 0.19.
    Returns
    -------
    out : (..., 3, ...) ndarray
        The image in XYZ format. Same dimensions as input.
    Raises
    ------
    ValueError
        If `rgb` is not at least 2-D with shape (..., 3, ...).
    Notes
    -----
    The CIE XYZ color space is derived from the CIE RGB color space. Note
    however that this function converts from sRGB.
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/CIE_1931_color_space
    Examples
    --------

    """
    # Follow the algorithm from http://www.easyrgb.com/index.php
    # except we don't multiply/divide by 100 in the conversion
    arr = _prepare_colorarray(rgb, channel_axis=-1).copy()
    mask = arr > 0.04045
    arr[mask] = np.power((arr[mask] + 0.055) / 1.055, 2.4)
    arr[~mask] /= 12.92
    return arr @ xyz_from_rgb.T.astype(arr.dtype)


def _prepare_colorarray(arr, force_copy=False, *, channel_axis=-1):
    """Check the shape of the array and convert it to
    floating point representation.
    """
    arr = np.asanyarray(arr)

    if arr.shape[channel_axis] != 3:
        msg = (f'the input array must have size 3 along `channel_axis`, '
               f'got {arr.shape}')
        raise ValueError(msg)

    float_dtype = _supported_float_type(arr.dtype)
    if float_dtype == np.float32:
        _func = dtype.img_as_float32
    else:
        _func = dtype.img_as_float64
    return _func(arr, force_copy=force_copy)

def _supported_float_type(input_dtype, allow_complex=False):
    """Return an appropriate floating-point dtype for a given dtype.
    float32, float64, complex64, complex128 are preserved.
    float16 is promoted to float32.
    complex256 is demoted to complex128.
    Other types are cast to float64.
    Parameters
    ----------
    input_dtype : np.dtype or Iterable of np.dtype
        The input dtype. If a sequence of multiple dtypes is provided, each
        dtype is first converted to a supported floating point type and the
        final dtype is then determined by applying `np.result_type` on the
        sequence of supported floating point types.
    allow_complex : bool, optional
        If False, raise a ValueError on complex-valued inputs.
    Returns
    -------
    float_type : dtype
        Floating-point dtype for the image.
    """
    if isinstance(input_dtype, Iterable) and not isinstance(input_dtype, str):
        return np.result_type(*(_supported_float_type(d) for d in input_dtype))
    input_dtype = np.dtype(input_dtype)
    if not allow_complex and input_dtype.kind == 'c':
        raise ValueError("complex valued input is not supported")
    return new_float_type.get(input_dtype.char, np.float64)

new_float_type = {
    # preserved types
    np.float32().dtype.char: np.float32,
    np.float64().dtype.char: np.float64,
    np.complex64().dtype.char: np.complex64,
    np.complex128().dtype.char: np.complex128,
    # altered types
    np.float16().dtype.char: np.float32,
    'g': np.float64,      # np.float128 ; doesn't exist on windows
    'G': np.complex128,   # np.complex256 ; doesn't exist on windows
}