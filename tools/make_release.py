from os import path
import PyInstaller.__main__
from shutil import copyfile
from pathlib import Path
from zipfile import ZipFile, ZIP_BZIP2
import platform

TOOL_DIR = Path(path.dirname(__file__))

if __name__ == '__main__':
    
    # Package the binary file
    PyInstaller.__main__.run([
        '--onefile',                            # Single file
        '--name=AutoDash-Pipeline',             # Executable name
        f'{TOOL_DIR}/make_release.spec',        # The spec file
    ])

    # Copy default_configuration.yml
    copyfile(f'{TOOL_DIR}/../default_configuration.yml', f'{TOOL_DIR}/dist/default_configuration.yml')
    
    # Zip all the files into package
    system = platform.system()
    arch = platform.architecture()
    zf = ZipFile(f'{TOOL_DIR}/dist/AutoDash-pipeline-release-{system}-{arch[0]}.zip', 'w')
    exe_file = 'AutoDash-pipeline'
    if system == 'Windows':
        exe_file += '.exe'
    zf.write(f'{TOOL_DIR}/dist/{exe_file}', compress_type=ZIP_BZIP2)
    zf.write(f'{TOOL_DIR}/dist/default_configuration.yml', compress_type=ZIP_BZIP2)
