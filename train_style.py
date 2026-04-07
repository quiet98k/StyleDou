import os

from style_modeling.dmc.arguments import parser
from style_modeling.dmc.dmc import train

if __name__ == "__main__":
    flags = parser.parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = flags.gpu_devices
    train(flags)
