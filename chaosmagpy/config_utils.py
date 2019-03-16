"""
Parameters and options in ChaosMagPy are stored in a dictionary and can be
modified as desired. The following list gives an overview of the possible
keywords.

**Parameters**

    params.r_surf : float
        Reference radius in kilometers (defaults to Earth's surface radius
        6371.2 km).
    params.dipole : list, ndarray, shape (3,)
        Coefficients of the dipole (used for GSM/SM coordinate
        transformations).
    params.version : str
        Default version of the CHAOS model, e.g. ``'6.x7'``.

**Files**

    files.RC_index : h5-file
        RC-index file (used for external field computation). See also
        :func:`data_utils.save_RC_h5file`.
    files.GSM_spectrum : npz-file
        GSM transformation coefficients. See also
        :func:`coordinate_utils.rotate_gauss_fft`.
    files.SM_spectrum : npz-file
        SM transformation coefficients. See also
        :func:`coordinate_utils.rotate_gauss_fft`.
    files.Earth_conductivity : txt-file
        Conductivity model of a layered Earth (used for induced fields).

"""

import os
import numpy as np

ROOT = os.path.abspath(os.path.dirname(__file__))
LIB = os.path.join(ROOT, 'lib')


# copied/inspired by matplotlib.rcsetup
def check_path_exists(s):
    """Check that path to file exists."""
    if s is None or s == 'None':
        return None
    if os.path.exists(s):
        return s
    else:
        raise FileNotFoundError(f'{s} does not exist.')


def check_float(s):
    """Convert to float."""
    try:
        return float(s)
    except ValueError:
        raise ValueError(f'Could not convert {s} to float.')


def check_string(s):
    """Convert to string."""
    try:
        return str(s)
    except ValueError:
        raise ValueError(f'Could not convert {s} to string.')


def check_vector(s, len=None):
    """Check that input is vector with required length."""
    try:
        s = np.array(s)
        assert s.ndim == 1
        if len is not None:
            if s.size != len:
                raise ValueError(f'Wrong length: {s.size} != {len}.')
        return s
    except Exception as err:
        raise ValueError(f'Not a valid vector. {err}')


DEFAULTS = {
    'params.r_surf': [6371.2, check_float],
    'params.dipole': [np.array([-29442.0, -1501.0, 4797.1]),
                      lambda x: check_vector(x, len=3)],
    'params.version': ['6.x7', check_string],

    # location of coefficient files
    'file.RC_index': [os.path.join(LIB, 'RC_index.h5'),
                      check_path_exists],
    'file.GSM_spectrum': [os.path.join(LIB, 'frequency_spectrum_gsm.npz'),
                          check_path_exists],
    'file.SM_spectrum': [os.path.join(LIB, 'frequency_spectrum_sm.npz'),
                         check_path_exists],
    'file.Earth_conductivity': [os.path.join(LIB, 'Earth_conductivity.dat'),
                                check_path_exists],  # placeholder
}


class ConfigCHAOS(dict):
    """Class for creating CHAOS configuration dictionary."""

    defaults = DEFAULTS

    def __init__(self, *args, **kwargs):
        super().update(*args, **kwargs)

    def __setitem__(self, key, value):
        """Set and check value before updating dictionary."""

        try:
            try:
                cval = self.defaults[key][1](value)
            except ValueError as err:
                raise ValueError(f'Key "{key}": {err}')
            super().__setitem__(key, cval)
        except KeyError:
            raise KeyError(f'"{key}" is not a valid parameter.')

    def __str__(self):
        return '\n'.join(map('{0[0]}: {0[1]}'.format, sorted(self.items())))

    def reset(self, key=None):
        """
        Load default values.

        Parameters
        ----------
        key : str, optional
            Single keyword that is reset (all keywords are reset by default).

        """
        if key is None:
            super().update(
                {key: val for key, (val, _) in self.defaults.items()})
        else:
            self.__setitem__(key, self.defaults[key][0])

    def load(self, filepath):
        """
        Load configuration dictionary from file and overwrite defaults.

        Parameters
        ----------
        filepath : str
            Filepath and name to configuration textfile.

        """

        with open(filepath, 'r') as f:
            for line in f.readlines():
                # skip comment lines
                if line[0] == '#':
                    continue

                key, value = line.split(' = ')
                value = value.split('#')[0].rstrip()  # remove comments and \n

                # check list input and convert to array
                if value[0] == '[' and value[-1] == ']':
                    value = np.fromstring(value[1:-1], sep=' ')

                self.__setitem__(key, value)
        f.close()

    def save(self, filepath):
        """
        Save configuration dictionary to a file.

        Parameters
        ----------
        filepath : str
            Filepath and name of the textfile that will be saved with the
            configuration values.

        """

        with open(filepath, 'w') as f:
            for key, value in self.items():
                f.write(f'{key} = {value}\n')
        f.close()
        print(f'Saved configuration textfile to {filepath}.')


# load defaults
configCHAOS = ConfigCHAOS({key: val for key, (val, _) in DEFAULTS.items()})


def rc(key, value):
    configCHAOS[key] = value


if __name__ == '__main__':
    # ensure default passes tests
    for key, (value, test) in DEFAULTS.items():
        if not test(value) == value:
            print(f"{key}: {test(value)} != {value}")