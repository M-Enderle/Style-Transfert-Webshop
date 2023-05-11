""" Prints the available cuda devices """

import torch

print(torch.cuda.device_count())
