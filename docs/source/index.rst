pyobs-gui
#########

This is a `pyobs <https://www.pyobs.org>`_ (`documentation <https://docs.pyobs.org>`_) module providing a GUI
for operating the whole system.


Example configuration
*********************

This is an example configuration for a GUI that defines one custom widget for the ``guiding`` module::

    class: pyobs_gui.GUI

    widgets:
      - module: guiding
        overwrite: True
        widget:
          class: mypackage.GuidingWidget

    comm:
      jid: test@example.com
      password: ***

    timezone: Europe/Berlin
    location:
      longitude: 9.944333
      latitude: 51.560583
      elevation: 201.

    vfs:
      class: pyobs.vfs.VirtualFileSystem
      roots:
        cache:
          class: pyobs.vfs.HttpFile
          download: http://localhost:37075/
        webcam:
          class: pyobs.vfs.HttpFile
          download: http://localhost:37077/


Available classes
*****************

There is one single class for the GUI.

GUI
===
.. autoclass:: pyobs_gui.GUI
   :members:
   :show-inheritance:
