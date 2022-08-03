from os.path import join
from time import time

import gphoto2 as gp2

CAMERA_TIMESTAMP_CONSTANT = 1.308617  # Laboratory calibrated hehe
CAMERAS_LABELS = {
    '203052002700': 'A',
    '203052002717': 'B'
}


class Photocicker:
    def __init__(self, usb_port):
        port_info_list = gp2.PortInfoList()
        port_info_list.load()
        abilities_list = gp2.CameraAbilitiesList()
        abilities_list.load()
        camera_list = abilities_list.detect(port_info_list)

        camera = gp2.Camera()
        idx = port_info_list.lookup_path(usb_port)
        camera.set_port_info(port_info_list[idx])
        idx = abilities_list.lookup_model(camera_list[0][0])
        camera.set_abilities(abilities_list[idx])

        # Get serial number
        camera_config = camera.get_config()
        _, serial = gp2.gp_widget_get_child_by_name(camera_config, 'eosserialnumber')
        self._name = CAMERAS_LABELS.get(serial.get_value())

        self._camera_handle = camera
        self._camera_config = camera_config

    def capture_image(self, photo_directory, verbose=False):
        if self._camera_handle is not None:
            timestamp = time() + CAMERA_TIMESTAMP_CONSTANT
            file_path = self._camera_handle.capture(gp2.GP_CAPTURE_IMAGE)
            target = join(photo_directory, f"{'%.4f' % timestamp}_{self._name}.jpg")
            camera_file = self._camera_handle.file_get(file_path.folder, file_path.name, gp2.GP_FILE_TYPE_NORMAL)
            camera_file.save(target)
            self._camera_handle.file_delete(file_path.folder, file_path.name)
            if verbose:
                print('cyknal ' + self._name)

    def close(self):
        self._camera_handle.exit()
        self._camera_handle = None

    def set_iso(self, value):
        ok, iso = gp2.gp_widget_get_child_by_name(self._camera_config, 'eosserialnumber')
        if ok >= gp2.GP_OK:
            iso.set_value(value)
            self._camera_handle.set_config(self._camera_config)
