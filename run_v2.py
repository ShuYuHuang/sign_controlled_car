# ******************************************************************************
#  Copyright (c) 2021. Kneron Inc. All rights reserved.                        *
# ******************************************************************************

import os
import sys
import platform
import argparse
import time
import numpy as np
import threading
from queue import Queue

PWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(PWD, '..'))

import kp
import cv2

SCPU_FW_PATH = os.path.join(PWD, '../kneron_plus/res/firmware/KL520/kdp2_fw_scpu.bin')
NCPU_FW_PATH = os.path.join(PWD, '../kneron_plus/res/firmware/KL520/kdp2_fw_ncpu.bin')
MODEL_FILE_PATH = os.path.join(PWD, '../kneron_plus/res/models/KL520/mobilnet_v2/models_520.nef')

_LOCK = threading.Lock()
_SEND_RUNNING = True
_RECEIVE_RUNNING = True
_ACTION_RUNNING = True

_image_to_inference = None
_image_to_show = None

_generic_raw_image_header = kp.GenericRawImageHeader()

from car import CarController
from time import sleep

c = CarController()
action={
    3:c.forward,
    1:c.left,
    0:c.right,
    2:c.still
}

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def _image_send_function(_device_group: kp.DeviceGroup) -> None:
    global _image_to_inference, _generic_raw_image_header, _SEND_RUNNING

    try:
        # set camera configuration
        if 'Windows' == platform.system():
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        try_cap_time = 0

        _generic_raw_image_header.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        _generic_raw_image_header.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        while _SEND_RUNNING:
            try:
                # read frame from camera
                if cap.isOpened():
                    ret, _image_to_inference = cap.read()

                    if not ret and try_cap_time < 50:
                        try_cap_time += 1
                        time.sleep(0.1)
                        continue
                    elif not ret:
                        print('Error: opencv open camera failed')
                        break
                    else:
                        try_cap_time = 0
                else:
                    print('Error: opencv open camera failed')
                    break
            except:
                print('Error: opencv read frame failed')
                break

            # convert color space to RGB565
            inference_image = cv2.cvtColor(src=_image_to_inference, code=cv2.COLOR_BGR2BGR565)

            # inference image
            if ret:
                kp.inference.generic_raw_inference_send(device_group=_device_group,
                                                        image=inference_image,
                                                        image_format=kp.ImageFormat.KP_IMAGE_FORMAT_RGB565,
                                                        generic_raw_image_header=_generic_raw_image_header)

        cap.release()
    except kp.ApiKPException as exception:
        print(' - Error: inference failed, error = {}'.format(exception))

    _SEND_RUNNING = False


def _result_receive_function(_device_group: kp.DeviceGroup,
                             _model_nef_descriptor: kp.ModelNefDescriptor, q) -> None:
    global _image_to_show, _generic_raw_image_header, _RECEIVE_RUNNING
    _loop = 0
    _fps = 0

    while _RECEIVE_RUNNING:
        time_start = time.time()

        # receive inference result
        try:
            generic_raw_result = kp.inference.generic_raw_inference_receive(device_group=_device_group,
                                                                             generic_raw_image_header=_generic_raw_image_header,
                                                                             model_nef_descriptor=_model_nef_descriptor)
        except kp.ApiKPException as exception:
            print(' - Error: inference failed, error = {}'.format(exception))
            exit(0)

        _loop += 1

        with _LOCK:
            temp_image = _image_to_inference.copy()

        # retrieve inference node output
        inf_node_output_list = []
        for node_idx in range(generic_raw_result.header.num_output_node):
            inference_float_node_output = kp.inference.generic_inference_retrieve_float_node(node_idx=node_idx,
                                                                                             generic_raw_result=generic_raw_result,
                                                                                             channels_ordering=kp.ChannelOrdering.KP_CHANNEL_ORDERING_CHW)
            inf_node_output_list.append(inference_float_node_output)

        conf = softmax(np.squeeze(inf_node_output_list[0].ndarray))    
        class_name = ['Right', 'Left', 'Stop', 'Background']
        pred_idx = int(inf_node_output_list[0].ndarray.argmax(1))
        if conf[pred_idx] > 0.9:
            pred_text = class_name[pred_idx] + ', ' + str(round(conf[pred_idx], 2))
        else:
            pred_text = 'Background'
            
        q.put((pred_idx, conf))
            
        time_end = time.time()

        if 30 == _loop:
            _fps = 1 / (time_end - time_start)
            _loop = 0
            
        # draw output class
        cv2.putText(img=temp_image,
                    text=pred_text,
                    org=(10, temp_image.shape[0] - 10),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=1,
                    color=(200, 200, 200),
                    thickness=1,
                    lineType=cv2.LINE_AA)
        # draw FPS
        cv2.putText(img=temp_image,
                    text='FPS: {:.2f}'.format(_fps),
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=1,
                    color=(200, 200, 200),
                    thickness=1,
                    lineType=cv2.LINE_AA)
        cv2.putText(img=temp_image,
                    text='Press \'ESC\' to exit',
                    org=(300, 30),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX,
                    fontScale=1,
                    color=(200, 200, 200),
                    thickness=1,
                    lineType=cv2.LINE_AA)

        with _LOCK:
            _image_to_show = temp_image.copy()

    _RECEIVE_RUNNING = False
    
def _action_function(q):
    global _ACTION_RUNNING
    while _ACTION_RUNNING:
        (pred_idx, conf) = q.get()
        print(pred_idx, conf)
        if conf[pred_idx] > 0.9:
            action[pred_idx]()
            sleep(0.01)
        else:
            action[3]()
            sleep(0.01)
            
    _ACTION_RUNNING = False



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='KL520 Demo Camera Generic Inference Example.')
    parser.add_argument('-p',
                        '--port_id',
                        help='Using specified port ID for connecting device (Default: port ID of first scanned Kneron '
                             'device)',
                        default=0,
                        type=int)
    args = parser.parse_args()

    usb_port_id = args.port_id

    """
    connect the device
    """
    try:
        print('[Connect Device]')
        device_group = kp.core.connect_devices(usb_port_ids=[usb_port_id])
        print(' - Success')
    except kp.ApiKPException as exception:
        print('Error: connect device fail, port ID = \'{}\', error msg: [{}]'.format(usb_port_id,
                                                                                     str(exception)))
        exit(0)

    """
    setting timeout of the usb communication with the device
    """
    print('[Set Device Timeout]')
    kp.core.set_timeout(device_group=device_group, milliseconds=10000)
    print(' - Success')

    """
    upload firmware to device
    """
    try:
        print('[Upload Firmware]')
        kp.core.load_firmware_from_file(device_group=device_group,
                                        scpu_fw_path=SCPU_FW_PATH,
                                        ncpu_fw_path=NCPU_FW_PATH)
        print(' - Success')
    except kp.ApiKPException as exception:
        print('Error: upload firmware failed, error = \'{}\''.format(str(exception)))
        exit(0)

    """
    upload model to device
    """
    try:
        print('[Upload Model]')
        model_nef_descriptor = kp.core.load_model_from_file(device_group=device_group,
                                                            file_path=MODEL_FILE_PATH)
        print(' - Success')

        print('[Model NEF Information]')
        print(model_nef_descriptor)
    except kp.ApiKPException as exception:
        print('Error: upload model failed, error = \'{}\''.format(str(exception)))
        exit(0)

    """
    prepare app generic inference config
    """
    _generic_raw_image_header = kp.GenericRawImageHeader(
        model_id=model_nef_descriptor.models[0].id,
        resize_mode=kp.ResizeMode.KP_RESIZE_ENABLE,
        padding_mode=kp.PaddingMode.KP_PADDING_CORNER,
        normalize_mode=kp.NormalizeMode.KP_NORMALIZE_KNERON
    )
    
    q = Queue()

    """
    starting inference work
    """
    print('[Starting Inference Work]')
    print(' - Starting inference')
    send_thread = threading.Thread(target=_image_send_function, args=(device_group,))
    receive_thread = threading.Thread(target=_result_receive_function, args=(device_group, model_nef_descriptor, q))
    action_thread = threading.Thread(target=_action_function, args=(q,))

    send_thread.start()
    receive_thread.start()
    action_thread.start()

    cv2.namedWindow('Generic Inference', cv2.WND_PROP_ASPECT_RATIO or cv2.WINDOW_GUI_EXPANDED)
    cv2.setWindowProperty('Generic Inference', cv2.WND_PROP_ASPECT_RATIO, cv2.WND_PROP_ASPECT_RATIO)

    while True:
        with _LOCK:
            if None is not _image_to_show:
                cv2.imshow('Generic Inference', _image_to_show)

        if (27 == cv2.waitKey(10)) or (not _SEND_RUNNING) or (not _RECEIVE_RUNNING) or (not _ACTION_RUNNING):
            break

    cv2.destroyAllWindows()

    _SEND_RUNNING = False
    _RECEIVE_RUNNING = False
    _ACTION_RUNNING = False

    send_thread.join()
    receive_thread.join()