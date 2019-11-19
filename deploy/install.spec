# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

appdata = [
    ('installer/templates', 'templates'),
    ('installer/static', 'static'),
    ('installer/templates', 'installer/templates'),
    ('installer/static', 'installer/static'),
]
a = Analysis(['install.py'],
             pathex=['C:\\Users\\nakamura9a\\Documents\\code\\git\\mdvr_plus\\deploy'],
             binaries=[],
             datas=appdata,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='install',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='icon.ico')
