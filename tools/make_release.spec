from PyInstaller.utils.hooks import copy_metadata, collect_data_files, collect_submodules
from os import path
from pathlib import Path

extra_files = copy_metadata('google-api-python-client') + collect_data_files('tensorflow', subdir=None, include_py_files=True)


a = Analysis(["../run"] + [ str(fp) for fp in Path('../src').rglob('*.py')],
             hiddenimports=collect_submodules('tensorflow') + ['scipy.special.cython_special'],
             hookspath=None,
             datas=extra_files,
             runtime_hooks=None)

for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='AutoDash-pipeline',
          debug=False,
          strip=None,
          upx=False,
          console=True )
