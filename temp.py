# from tensorflow.python.client import device_lib
# print(device_lib.list_local_devices())

# import tensorflow as tf
# import os

# os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

# if tf.test.gpu_device_name():
#     print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))
# else:
#     print("Please install GPU version of TF")

import tensorflow as tf
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
