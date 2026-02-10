# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[
                'pandas._libs.tslibs.timedeltas',
                'pandas._libs.tslibs.nattype',
                'pandas._libs.tslibs.np_datetime',
                'pandas._libs.tslibs.offsets',
                'pandas._libs.tslibs.period',
                'pandas._libs.tslibs.strptime',
                'pandas._libs.tslibs.timestamps',
                'pandas._libs.tslibs.timezones',
                'pandas._libs.tslibs.tzconversion',
                'psycopg2._psycopg',
                'openpyxl',
                'tkcalendar',
                'customtkinter',
                'pdfminer',
                'unidecode',
                'tkinter-tooltip'
             ],
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
          name='ProcesadorDeFacturas',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, # True para ver la consola de depuración, False para ocultarla
          icon='favicon.ico') # Puedes añadir la ruta a un archivo .ico si quieres un icono personalizado