from dataclasses import dataclass
from pathlib import Path

import netCDF4 as nc
import pandas as pd


def parse_file(file):
    variables = []
    with nc.Dataset(file, 'r') as ds:
        dims = ds.dimensions
        for variable in ds.variables:
            if (
                variable not in dims
                and 'time' not in variable
                and 'time' in ds.variables[variable].dimensions
            ):
                variables.append(variable)

    return tuple(variables)


@dataclass
class Case:
    """
    This class generates a catalog for a given CESM casename.

    Parameters
    ----------
    casename : str
    archive_log_dir : str
    run_dir : str
    hist_dirs : list
    streams : list
    components : list
    """

    casename: str
    archive_log_dir: str
    run_dir: str
    hist_dirs: list
    streams: list
    components: list = None

    def __post_init__(self):
        self.archive_log_dir = Path(self.archive_log_dir)
        self.run_dir = Path(self.run_dir)
        self.hist_dirs = list(map(lambda x: Path(x), self.hist_dirs))
        self.streams.sort()
        assert self.archive_log_dir.exists()
        assert self.run_dir.exists()
        for hist_dir in self.hist_dirs:
            assert hist_dir.exists()

    def build(self):
        self._find_log_files()
        self._parse_log_files()
        self._find_and_parse_hist_files()
        return self

    def _find_log_files(self):
        """
        Look in rundir and archive for log files
        """
        self.log_files = []
        dirs = [self.run_dir, self.archive_log_dir]
        if self.components:
            for component in self.components:
                for directory in dirs:
                    self.log_files.extend(list(directory.rglob(f'{component}.log.*')))

        else:
            for directory in dirs:
                self.log_files.extend(list(directory.rglob('*.log.*')))

        self.log_files.sort()

    def _parse_log_files(self):
        entries = []
        for file in self.log_files:
            component = file.parts[-1].split('.')[0]
            entries.append({'component': component, 'log_file': file.as_posix()})
        self.log_filenames = pd.DataFrame(entries).set_index('component')

    def _find_and_parse_hist_files(self):

        """
        Look in rundir and archive for history files and parse them.
        """
        dfs = []
        self.hist_files = []
        dirs = self.hist_dirs + [self.run_dir]
        for stream in sorted(self.streams):
            files = []
            for directory in dirs:
                files.extend(list(directory.rglob(f'{self.casename}.{stream}.[0-9]*.nc')))
            df = pd.DataFrame()
            df['path'] = list(map(lambda x: x.as_posix(), files))
            df['variable'] = list(map(parse_file, files))
            df['timestamp'] = list(map(lambda x: x.stem.split('.')[-1], files))
            df['stream'] = stream
            df['casename'] = self.casename
            dfs.append(df)

        self.df = pd.concat(dfs).sort_values(by=['path', 'stream']).reset_index(drop=True)
