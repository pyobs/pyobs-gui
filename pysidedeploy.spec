[app]

# title of your application
title = pyobs-gui

# project root directory. default = The parent directory of input_file
project_dir = .

# source file entry point path. default = main.py
input_file = pyobs_gui

# directory where the executable output is generated
exec_directory = dist

# path to the project file relative to project_dir
project_file = 

# application icon
icon = /home/husser/code/pyobs/pyobs-gui/.venv/lib/python3.13/site-packages/PySide6/scripts/deploy_lib/pyside_icon.jpg

[python]

# python path
python_path = /home/husser/code/pyobs/pyobs-gui/.venv/bin/python3

# python packages to install
packages = Nuitka==4.0

# buildozer = for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]

# paths to required qml files. comma separated
# normally all the qml files required by the project are added automatically
# design studio projects include the qml files using qt resources
qml_files = 

# excluded qml plugin binaries
excluded_qml_plugins = 

# qt modules used. comma separated
modules = Core,DBus,Designer,Gui,Network,OpenGL,OpenGLWidgets,Widgets,Xml

# qt plugins used by the application. only relevant for desktop deployment
# for qt plugins used in android application see [android][plugins]
plugins = accessiblebridge,designer,egldeviceintegrations,generic,iconengines,imageformats,networkaccess,networkinformation,platforminputcontexts,platforms,platforms/darwin,platformthemes,styles,tls,wayland-decoration-client,wayland-graphics-integration-client,wayland-shell-integration,xcbglintegrations

[android]

# path to pyside wheel
wheel_pyside = 

# path to shiboken wheel
wheel_shiboken = 

# plugins to be copied to libs folder of the packaged application. comma separated
plugins = 

[nuitka]

# usage description for permissions requested by the app as found in the info.plist file
# of the app bundle. comma separated
# eg = extra_args = --show-modules --follow-stdlib
macos.permissions = 

# mode of using nuitka. accepts standalone or onefile. default = onefile
mode = standalone

# specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations --clang --python-flag=-m --include-package=astropy.units.format --include-package=astropy.units.format.generic_parsetab --include-package=astropy.units.format.generic_lextab --include-package=astropy.units.format.cds_parsetab --include-package=astropy.units.format.cds_lextab --include-package=astropy.units.format.ogip_parsetab --include-package=astropy.units.format.ogip_lextab --include-package=astropy.coordinates.angles --include-package=astropy.coordinates.angles.angle_parsetab --include-package=astropy.coordinates.angles.angle_lextab --include-package=astropy.extern.ply --include-package-data=asdf --include-package-data=astropy --include-package-data=sunpy --include-package-data=matplotlib --include-package-data=qfitswidget --include-package-data=astropy_iers_data --include-package=pyobs.vfs --include-package-data=astroquery

[buildozer]

# build mode
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
# release creates a .aab, while debug creates a .apk
mode = debug

# path to pyside6 and shiboken6 recipe dir
recipe_dir = 

# path to extra qt android .jar files to be loaded by the application
jars_dir = 

# if empty, uses default ndk path downloaded by buildozer
ndk_path = 

# if empty, uses default sdk path downloaded by buildozer
sdk_path = 

# other libraries to be loaded at app startup. comma separated.
local_libs = 

# architecture of deployed platform
arch = 

