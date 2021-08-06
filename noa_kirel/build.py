import os
import sys

import PyInstaller.__main__

package = 'noa_kirel'

if len(sys.argv) > 1:
    name = f'{package}-{sys.argv[1]}'
else:
    name = package

PyInstaller.__main__.run([
    '--name={}'.format(name),
    '--onefile',
    '--windowed',
    os.path.join(package, '__main__.py')
])
