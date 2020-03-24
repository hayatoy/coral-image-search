from threading import Lock
import tflite_runtime.interpreter as tflite
import tensorflow as tf
import numpy as np
import platform

EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]

DELEGATES = {
  "tpu": 0,
  "cpu": 1
}

TFLITE_PATH = "mobilenet_v1_1.0_224_quant_embedding_extractor.tflite"
TFLITE_TPU_PATH = "mobilenet_v1_1.0_224_quant_embedding_extractor_edgetpu.tflite"

class Inference(object):
  """ """

  def __init__(self):
    self.interpreter_lock = Lock()
    self.interpreter = None
    self.input_index = None
    self.output_index = None
    self.interpreters = [None]*2
    self.input_indexes = [None]*2
    self.output_indexes = [None]*2
    self.init_interpreter()

  def init_interpreter(self, delegate='tpu'):
    """ Initialize interpreter
        delegate: delegate name. refer to DELEGATES
    """
    if not not self.interpreter:
      return
    with self.interpreter_lock:
      print("Edge TPU delegate")
      self.interpreters[DELEGATES['tpu']] = tflite.Interpreter(
        model_path=TFLITE_TPU_PATH,
        experimental_delegates=[tflite.load_delegate(EDGETPU_SHARED_LIB, {})])
      self.interpreters[DELEGATES['tpu']].allocate_tensors()
      input_details = self.interpreters[DELEGATES['tpu']].get_input_details()
      output_details = self.interpreters[DELEGATES['tpu']].get_output_details()
      self.input_indexes[DELEGATES['tpu']] = input_details[0]['index']
      self.output_indexes[DELEGATES['tpu']] = output_details[0]['index']

      print("init interpreter_cpu")
      self.interpreters[DELEGATES['cpu']] = tf.lite.Interpreter(
          model_path=TFLITE_PATH)
      self.interpreters[DELEGATES['cpu']].allocate_tensors()
      input_details = self.interpreters[DELEGATES['cpu']].get_input_details()
      output_details = self.interpreters[DELEGATES['cpu']].get_output_details()
      self.input_indexes[DELEGATES['cpu']] = input_details[0]['index']
      self.output_indexes[DELEGATES['cpu']] = output_details[0]['index']

    self.change_interpreter(delegate)
    print(input_details)

  def change_interpreter(self, delegate='tpu'):
    """ Change interpreter type
        delegate: delegate name. refer to DELEGATES
    """
    with self.interpreter_lock:
      print('change_interpreter')
      self.interpreter = self.interpreters[DELEGATES[delegate]]
      self.input_index = self.input_indexes[DELEGATES[delegate]]
      self.output_index = self.output_indexes[DELEGATES[delegate]]

  def extract_feature(self, img):
    """ Extract feature from image
        img: PIL Image
    """
    with self.interpreter_lock:
      # Feed image data to interpreter
      input_data = np.array(img)
      input_data = np.expand_dims(input_data, axis=0)
      self.interpreter.set_tensor(self.input_index, input_data)

      # Invoke inference
      self.interpreter.invoke()

      # Get inference output
      output_data = self.interpreter.get_tensor(self.output_index)
      output_data = output_data.reshape((1, 1024))
      return output_data
