from multiprocessing import Process
# import logging
from sys import argv

# import gphoto2 as gp
from gphoto2 import Camera

from photocicker import Photocicker

if __name__ == '__main__':
    images_directory = argv[1]

    # # Turn on logs
    # logging.basicConfig(
    #     format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    # logging.basicConfig(
    #     format='%(levelname)s: %(name)s: %(message)s', level=logging.DEBUG)
    # callback_obj = gp.check_result(gp.use_python_logging())

    # Initialize cameras
    camera_ports = list(Camera.autodetect())
    if len(camera_ports) == 0:
        print('No cameras detected')
        exit(1)

    camera_ports = [x[1] for x in camera_ports]
    cameras = [Photocicker(x) for x in camera_ports]

    # Cik photo
    processes = []
    for i, c in enumerate(cameras):
        process = Process(target=c.capture_image, args=(images_directory, True))
        process.start()
        processes.append(process)

    for p in processes:
        p.join()
        p.close()

    # Release cameras
    for c in cameras:
        c.close()

    exit(0)
