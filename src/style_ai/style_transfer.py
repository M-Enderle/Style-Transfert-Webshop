"""
Style transfer implementation using strotss
"""

# TODO Flo: Typing!

from argparse import ArgumentParser
from time import time

import numpy as np
import torch
from PIL import Image
from torch import nn, optim
from torchvision import models
from tqdm import tqdm

from style_ai.utils import (calculate_loss, fold_laplace_pyramid, laplacian,
                            load_image, make_laplace_pyramid, np_to_pil,
                            np_to_tensor, pil_resize_long_edge_to, pil_to_np,
                            sample_indices, tensor_resample, tensor_to_np)


class Vgg16Extractor(nn.Module):
    """
    VGG16 feature extractor for style transfer
    """

    def __init__(self, space):
        super().__init__()
        self.vgg_layers = models.vgg16(weights=models.VGG16_Weights.DEFAULT).features

        for param in self.parameters():
            param.requires_grad = False
        self.capture_layers = [1, 3, 6, 8, 11, 13, 15, 22, 29]
        self.space = space

    def forward_base(self, tensor):
        """
        Forward pass for feature extraction
        :params:
            tensor: input tensor
        :returns:
            extracted features at capture layers
        """
        feat = [tensor]
        for i, layer in enumerate(self.vgg_layers):
            tensor = layer(tensor)
            if i in self.capture_layers:
                feat.append(tensor)
        return feat

    def forward(self, tensor):
        """
        Forward pass for feature extraction
        :params:
            tensor: input tensor
        :returns:
            extracted features
        """
        if self.space != "vgg":
            tensor = (tensor + 1.0) / 2.0
            tensor = tensor - (
                torch.Tensor([0.485, 0.456, 0.406]).to(tensor.device).view(1, -1, 1, 1)
            )
            tensor = tensor / (
                torch.Tensor([0.229, 0.224, 0.225]).to(tensor.device).view(1, -1, 1, 1)
            )
        feat = self.forward_base(tensor)
        return feat

    def forward_samples_hypercolumn(self, input_tensor, samps=100):
        """
        Forward pass for sampling hypercolumn features
        :params:
            input_tensor: input tensor
            samps: number of samples
        :returns:
            sampled features
        """
        feat = self.forward(input_tensor)

        x_indices, y_indices = np.meshgrid(
            np.arange(input_tensor.shape[2]), np.arange(input_tensor.shape[3])
        )
        x_indices = np.expand_dims(x_indices.flatten(), 1)
        y_indices = np.expand_dims(y_indices.flatten(), 1)
        indices = np.concatenate([x_indices, y_indices], 1)

        samples = min(samps, indices.shape[0])

        np.random.shuffle(indices)
        x_indices = indices[:samples, 0]
        y_indices_sampled = indices[:samples, 1]

        feat_samples = []
        for i, layer_feat in enumerate(feat):
            # hack to detect lower resolution
            if i > 0 and layer_feat.size(2) < feat[i - 1].size(2):
                x_indices = x_indices / 2.0
                y_indices_sampled = y_indices_sampled / 2.0

            x_indices = np.clip(x_indices, 0, layer_feat.shape[2] - 1).astype(np.int32)
            y_indices_sampled = np.clip(
                y_indices_sampled, 0, layer_feat.shape[3] - 1
            ).astype(np.int32)

            features = layer_feat[
                :, :, x_indices[range(samples)], y_indices_sampled[range(samples)]
            ]
            feat_samples.append(features.clone().detach())

        feat = torch.cat(feat_samples, 1)
        return feat


def optimize(res, content, style, w_content, learning_rate, extractor):
    """
    Optimizes the result image
    :params:
        res: result image
        content: content image
        style: style image
        w_content: content weight
        learning_rate: learning rate
        extractor: feature extractor
    :returns:
        stylized image
    """
    # torch.autograd.set_detect_anomaly(True)
    result_pyramid = make_laplace_pyramid(res, 5)
    result_pyramid = [l.data.requires_grad_() for l in result_pyramid]

    opt_iter = 200
    # if scale == 1:
    #     opt_iter = 800

    # use rmsprop
    optimizer = optim.RMSprop(result_pyramid, lr=learning_rate)

    # extract features for content
    feat_content = extractor(content)

    stylized = fold_laplace_pyramid(result_pyramid)
    # let's ignore the regions for now
    # some inner loop that extracts samples
    feat_style = None
    for _ in range(5):
        with torch.no_grad():
            # r is region of interest (mask)
            feat_e = extractor.forward_samples_hypercolumn(style, samps=1000)
            feat_style = (
                feat_e if feat_style is None else torch.cat((feat_style, feat_e), dim=2)
            )
    # feat_style.requires_grad_(False)

    # init indices to optimize over
    x_indices, y_indices = sample_indices(
        feat_content[0]
    )  # 0 to sample over first layer extracted
    for iteration in tqdm(range(opt_iter)):
        optimizer.zero_grad()

        stylized = fold_laplace_pyramid(result_pyramid)
        # original code has resample here, seems pointless with uniform shuffle
        # ...
        # also shuffle them every y iter
        if iteration != 0:
            np.random.shuffle(x_indices)
            np.random.shuffle(y_indices)
        feat_result = extractor(stylized)

        loss = calculate_loss(
            feat_result, feat_content, feat_style, [x_indices, y_indices], w_content
        )
        loss.backward()
        optimizer.step()
    return stylized


def strotss(
    content_pil,
    style_pil,
    content_weight=1.0 * 16.0,
    extractor: Vgg16Extractor = None,
    device="cuda:0",
    space="uniform",
):
    """
    Strotss implementation
    :params:
        content_pil: PIL image of content
        style_pil: PIL image of style
        content_weight: weight of content loss
        device: device to run on
        space: color space to use
    :returns:
        stylized image
    """
    content_np = pil_to_np(content_pil)
    style_np = pil_to_np(style_pil)
    content_full = np_to_tensor(content_np, space).to(device)
    style_full = np_to_tensor(style_np, space).to(device)

    learning_rate = 2e-3

    if extractor is None:
        extractor = Vgg16Extractor(space=space)

    extractor.to(device)

    scales = []
    for scale in range(10):
        divisor = 2**scale
        if min(content_pil.width, content_pil.height) // divisor >= 33:
            scales.insert(0, divisor)

    for scale in scales:
        # rescale content to current scale
        content = tensor_resample(
            content_full,
            [content_full.shape[2] // scale, content_full.shape[3] // scale],
        )
        style = tensor_resample(
            style_full, [style_full.shape[2] // scale, style_full.shape[3] // scale]
        )
        print(f"Optimizing at resoluton [{content.shape[2]}, {content.shape[3]}]")

        # upsample or initialize the result
        if scale == scales[0]:
            # first
            result = laplacian(content) + style.mean(2, keepdim=True).mean(
                3, keepdim=True
            )
        elif scale == scales[-1]:
            # last
            result = tensor_resample(result, [content.shape[2], content.shape[3]])
            learning_rate = 1e-3
        else:
            result = tensor_resample(
                result, [content.shape[2], content.shape[3]]
            ) + laplacian(content)

        # do the optimization on this scale
        result = optimize(
            result,
            content,
            style,
            w_content=content_weight,
            learning_rate=learning_rate,
            extractor=extractor,
        )

        # next scale lower weight
        content_weight /= 2.0

    clow = -1.0 if space == "uniform" else -1.7
    chigh = 1.0 if space == "uniform" else 1.7
    result_np = tensor_to_np(
        tensor_resample(
            torch.clamp(result, clow, chigh),
            [content_full.shape[2], content_full.shape[3]],
        )
    )
    # renormalize image
    result_np -= result_np.min()
    result_np /= result_np.max()
    return np_to_pil(result_np * 255.0)


def style_transfer(
    content: Image,
    style: Image,
    extractor: Vgg16Extractor = None,
    weight: float = 1.5,
    device: str = "cuda:0",
    resize_to: int = 512,
) -> Image:
    """
    Stylize content image with style image
    :params:
        content: content image
        style: style image
        weight: weight of content loss
        output: output file name
        device: device to run on
        resize_to: resize to this size before stylizing
    :returns:
        stylized image
    """
    content = pil_resize_long_edge_to(content, resize_to)
    style = pil_resize_long_edge_to(style, resize_to)
    stylized = strotss(
        content, style, content_weight=weight, extractor=extractor, device=device
    )
    return stylized


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("content", type=str)
    parser.add_argument("style", type=str)
    parser.add_argument("--weight", type=float, default=1.0)
    parser.add_argument("--output", type=str, default="strotss.png")
    parser.add_argument("--device", type=str, default="cuda:0")
    # uniform ospace = optimization done in [-1, 1], else imagenet normalized space
    parser.add_argument(
        "--ospace", type=str, default="uniform", choices=["uniform", "vgg"]
    )
    parser.add_argument("--resize_to", type=int, default=512)
    args = parser.parse_args()

    # make 256 the smallest possible long side, will still fail if short side is <
    args.resize_to = max(2**8, args.resize_to)

    content_pillow, style_pillow = load_image(args.content), load_image(args.style)
    args.weight *= 16.0

    start = time()
    result_image = strotss(
        pil_resize_long_edge_to(content_pillow, args.resize_to),
        pil_resize_long_edge_to(style_pillow, args.resize_to),
        args.weight,
        args.device,
        args.ospace,
    )
    result_image.save(args.output)
    print(f"Done in {time()-start:.3f}s")
