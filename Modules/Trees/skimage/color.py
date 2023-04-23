import functools
from collections.abc import Iterable

import numpy as np
from Modules.Trees.skimage import dtype
xyz_from_rgb = np.array([[0.412453, 0.357580, 0.180423],
                         [0.212671, 0.715160, 0.072169],
                         [0.019334, 0.119193, 0.950227]])
illuminants = \
    {"A": {'2': (1.098466069456375, 1, 0.3558228003436005),
           '10': (1.111420406956693, 1, 0.3519978321919493),
           'R': (1.098466069456375, 1, 0.3558228003436005)},
     "B": {'2': (0.9909274480248003, 1, 0.8531327322886154),
           '10': (0.9917777147717607, 1, 0.8434930535866175),
           'R': (0.9909274480248003, 1, 0.8531327322886154)},
     "C": {'2': (0.980705971659919, 1, 1.1822494939271255),
           '10': (0.9728569189782166, 1, 1.1614480488951577),
           'R': (0.980705971659919, 1, 1.1822494939271255)},
     "D50": {'2': (0.9642119944211994, 1, 0.8251882845188288),
             '10': (0.9672062750333777, 1, 0.8142801513128616),
             'R': (0.9639501491621826, 1, 0.8241280285499208)},
     "D55": {'2': (0.956797052643698, 1, 0.9214805860173273),
             '10': (0.9579665682254781, 1, 0.9092525159847462),
             'R': (0.9565317453467969, 1, 0.9202554587037198)},
     "D65": {'2': (0.95047, 1., 1.08883),   # This was: `lab_ref_white`
             '10': (0.94809667673716, 1, 1.0730513595166162),
             'R': (0.9532057125493769, 1, 1.0853843816469158)},
     "D75": {'2': (0.9497220898840717, 1, 1.226393520724154),
             '10': (0.9441713925645873, 1, 1.2064272211720228),
             'R': (0.9497220898840717, 1, 1.226393520724154)},
     "E": {'2': (1.0, 1.0, 1.0),
           '10': (1.0, 1.0, 1.0),
           'R': (1.0, 1.0, 1.0)}}

class channel_as_last_axis:
    """Decorator for automatically making channels axis last for all arrays.
    This decorator reorders axes for compatibility with functions that only
    support channels along the last axis. After the function call is complete
    the channels axis is restored back to its original position.
    Parameters
    ----------
    channel_arg_positions : tuple of int, optional
        Positional arguments at the positions specified in this tuple are
        assumed to be multichannel arrays. The default is to assume only the
        first argument to the function is a multichannel array.
    channel_kwarg_names : tuple of str, optional
        A tuple containing the names of any keyword arguments corresponding to
        multichannel arrays.
    multichannel_output : bool, optional
        A boolean that should be True if the output of the function is not a
        multichannel array and False otherwise. This decorator does not
        currently support the general case of functions with multiple outputs
        where some or all are multichannel.
    """
    def __init__(self, channel_arg_positions=(0,), channel_kwarg_names=(),
                 multichannel_output=True):
        self.arg_positions = set(channel_arg_positions)
        self.kwarg_names = set(channel_kwarg_names)
        self.multichannel_output = multichannel_output

    def __call__(self, func):

        @functools.wraps(func)
        def fixed_func(*args, **kwargs):

            channel_axis = kwargs.get('channel_axis', None)

            if channel_axis is None:
                return func(*args, **kwargs)

            # TODO: convert scalars to a tuple in anticipation of eventually
            #       supporting a tuple of channel axes. Right now, only an
            #       integer or a single-element tuple is supported, though.
            if np.isscalar(channel_axis):
                channel_axis = (channel_axis,)
            if len(channel_axis) > 1:
                raise ValueError(
                    "only a single channel axis is currently supported")

            if channel_axis == (-1,) or channel_axis == -1:
                return func(*args, **kwargs)

            if self.arg_positions:
                new_args = []
                for pos, arg in enumerate(args):
                    if pos in self.arg_positions:
                        new_args.append(np.moveaxis(arg, channel_axis[0], -1))
                    else:
                        new_args.append(arg)
                new_args = tuple(new_args)
            else:
                new_args = args

            for name in self.kwarg_names:
                kwargs[name] = np.moveaxis(kwargs[name], channel_axis[0], -1)

            # now that we have moved the channels axis to the last position,
            # change the channel_axis argument to -1
            kwargs["channel_axis"] = -1

            # Call the function with the fixed arguments
            out = func(*new_args, **kwargs)
            if self.multichannel_output:
                out = np.moveaxis(out, -1, channel_axis[0])
            return out

        return fixed_func

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
def get_xyz_coords(illuminant, observer, dtype=float):
    """Get the XYZ coordinates of the given illuminant and observer [1]_.
    Parameters
    ----------
    illuminant : {"A", "B", "C", "D50", "D55", "D65", "D75", "E"}, optional
        The name of the illuminant (the function is NOT case sensitive).
    observer : {"2", "10", "R"}, optional
        One of: 2-degree observer, 10-degree observer, or 'R' observer as in
        R function grDevices::convertColor.
    dtype: dtype, optional
        Output data type.
    Returns
    -------
    out : array
        Array with 3 elements containing the XYZ coordinates of the given
        illuminant.
    Raises
    ------
    ValueError
        If either the illuminant or the observer angle are not supported or
        unknown.
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Standard_illuminant
    """
    illuminant = illuminant.upper()
    observer = observer.upper()
    try:
        return np.asarray(illuminants[illuminant][observer], dtype=dtype)
    except KeyError:
        raise ValueError(f'Unknown illuminant/observer combination '
                         f'(`{illuminant}`, `{observer}`)')
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

