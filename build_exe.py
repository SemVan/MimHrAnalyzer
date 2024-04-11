import PyInstaller.__main__

# Если получите ошибку
# pkg_resources.DistributionNotFound: The 'google-cloud-core' distribution was not found and is required by the application
# Установите
# pip install google-cloud-core

PyInstaller.__main__.run([
    'build.spec',
    # '--onefile',
    #'--windowed',
    #'--noconfirm',
])
