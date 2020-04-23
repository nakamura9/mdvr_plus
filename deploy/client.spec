# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['client.py'],
             #pathex=['F:\\Documents\\code\\git\\mdvr_plus\\deploy'],
             #binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=["."],
             #runtime_hooks=[],
             #excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             #noarchive=False
             )

if not os.environ.get("PYINSTALLER_CEFPYTHON3_HOOK_SUCCEEDED", None):
    raise SystemExit("Error: Pyinstaller hook-cefpython3.py script was "
                     "not executed or it failed")

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='client',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               #upx_exclude=[],
               name='client')
