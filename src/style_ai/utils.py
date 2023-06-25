"""
Utils for style transfer
"""

import math

import numpy as np
import torch
from PIL import Image
from torch.nn import functional as F
from torchvision import transforms


# PIL utils
def load_image(path):
    """
    Load image from path
    :params:
        path: str, path to image
    :return:
        PIL.Image object
    """
    with open(path, "rb") as file:
        img = Image.open(file)
        return img.convert("RGB")


def pil_resize_long_edge_to(pil, trg_size):
    """
    Resize PIL image so that long edge is equal to trg_size
    :params:
        pil: PIL.Image object
        trg_size: int, target size of long edge
    :return:
        resized PIL.Image object
    """
    short_w = pil.width < pil.height
    ar_resized_long = (trg_size / pil.height) if short_w else (trg_size / pil.width)
    resized = pil.resize(
        (int(pil.width * ar_resized_long), int(pil.height * ar_resized_long)),
        Image.BICUBIC,
    )
    return resized


def np_to_pil(npy):
    """
    Convert numpy array to PIL.Image object
    :params:
        npy: numpy array
    :return:
        PIL.Image object
    """
    return Image.fromarray(npy.astype(np.uint8))


def pil_to_np(pil):
    """
    Convert PIL.Image object to numpy array
    :params:
        pil: PIL.Image object
    :return:
        numpy array
    """
    return np.array(pil)


# Torch utils


def tensor_to_np(tensor, cut_dim_to_3=True):
    """
    Convert torch.Tensor to numpy array
    :params:
        tensor: torch.Tensor object
        cut_dim_to_3: bool, if True, cut first dimension of tensor
    :return:
        numpy array
    """
    if len(tensor.shape) == 4:
        if cut_dim_to_3:
            tensor = tensor[0]
        else:
            return tensor.data.cpu().numpy().transpose((0, 2, 3, 1))
    return tensor.data.cpu().numpy().transpose((1, 2, 0))


def np_to_tensor(npy, space):
    """
    Convert numpy array to torch.Tensor
    :params:
        npy: numpy array
        space: str, color space of image
    :return:
        torch.Tensor object of numpy array
    """
    if space == "vgg":
        pil = np_to_pil(npy)
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
        return transform(pil).unsqueeze(0)
    return (
        (torch.Tensor(npy.astype(float) / 127.5) - 1.0).permute((2, 0, 1)).unsqueeze(0)
    )


def tensor_resample(tensor, dst_size, mode="bilinear") -> torch.Tensor:
    """
    Resample torch.Tensor object
    :params:
        tensor: torch.Tensor object
        dst_size: tuple, target size of tensor
        mode: str, mode of resampling
    :return:
        resampled torch.Tensor object
    """
    return F.interpolate(tensor, size=dst_size, mode=mode, align_corners=False)


# Laplacian Pyramid


def laplacian(tensor):
    """
    Compute Laplacian of torch.Tensor object
    :params:
        tensor: torch.Tensor object
    :return:
        Laplacian of tensor
    """
    return tensor - tensor_resample(
        tensor_resample(tensor, [tensor.shape[2] // 2, tensor.shape[3] // 2]),
        [tensor.shape[2], tensor.shape[3]],
    )


def make_laplace_pyramid(tensor, levels):
    """
    Make Laplacian pyramid of torch.Tensor object
    :params:
        tensor: torch.Tensor object
        levels: int, number of levels of pyramid
    :return:
        list of torch.Tensor objects (laplacian pyramid)
    """
    pyramid = []
    current = tensor
    for _ in range(levels):
        pyramid.append(laplacian(current))
        current = tensor_resample(
            current, (max(current.shape[2] // 2, 1), max(current.shape[3] // 2, 1))
        )
    pyramid.append(current)
    return pyramid


def fold_laplace_pyramid(pyramid):
    """
    Fold Laplacian pyramid
    :params:
        pyramid: list of torch.Tensor objects (laplacian pyramid)
    :return:
        torch.Tensor object (folded pyramid)
    """
    current = pyramid[-1]
    for i in range(len(pyramid) - 2, -1, -1):
        up_h, up_w = pyramid[i].shape[2], pyramid[i].shape[3]
        current = pyramid[i] + tensor_resample(current, (up_h, up_w))
    return current


# Distance utils


def pairwise_distances_cos(tensor_x, tensor_y):
    """
    Compute pairwise cosine distances between two torch.Tensor objects
    :params:
        tensor_x: torch.Tensor object
        tensor_y: torch.Tensor object
    :return:
        torch.Tensor object of pairwise cosine distances
    """
    x_norm = torch.sqrt((tensor_x**2).sum(1).view(-1, 1))
    y_t = torch.transpose(tensor_y, 0, 1)
    y_norm = torch.sqrt((tensor_y**2).sum(1).view(1, -1))
    dist = 1.0 - torch.mm(tensor_x, y_t) / x_norm / y_norm
    return dist


def pairwise_distances_sq_l2(tensor_x, tensor_y):
    """
    Compute pairwise squared L2 distances between two torch.Tensor objects
    :params:
        tensor_x: torch.Tensor object
        tensor_y: torch.Tensor object
    :return:
        torch.Tensor object of pairwise squared L2 distances
    """
    x_norm = (tensor_x**2).sum(1).view(-1, 1)
    y_t = torch.transpose(tensor_y, 0, 1)
    y_norm = (tensor_y**2).sum(1).view(1, -1)
    dist = x_norm + y_norm - 2.0 * torch.mm(tensor_x, y_t)
    return torch.clamp(dist, 1e-5, 1e5) / tensor_x.size(1)


def distmat(tensor_x, tensor_y, cos_d=True):
    """
    Compute distance matrix between two torch.Tensor objects
    :params:
        tensor_x: torch.Tensor object
        tensor_y: torch.Tensor object
        cos_d: bool, if True, compute cosine distance, else compute squared L2 distance
    :return:
        torch.Tensor object of distance matrix
    """
    if cos_d:
        distance_matrix = pairwise_distances_cos(tensor_x, tensor_y)
    else:
        distance_matrix = torch.sqrt(pairwise_distances_sq_l2(tensor_x, tensor_y))
    return distance_matrix


def content_loss(feat_result, feat_content):
    """
    Compute content loss between two torch.Tensor objects
    :params:
        feat_result: torch.Tensor object
        feat_content: torch.Tensor object
    :return:
        torch.Tensor object of content loss
    """
    distance = feat_result.size(1)

    feat_result_transposed = (
        feat_result.transpose(0, 1).contiguous().view(distance, -1).transpose(0, 1)
    )
    feat_content_transposed = (
        feat_content.transpose(0, 1).contiguous().view(distance, -1).transpose(0, 1)
    )

    feat_content_transposed = feat_content_transposed[:, :-2]
    feat_result_transposed = feat_result_transposed[:, :-2]

    matrix_feat_res = distmat(feat_result_transposed, feat_result_transposed)

    matrix_feat_cont = distmat(feat_content_transposed, feat_content_transposed)

    distance = torch.abs(matrix_feat_res - matrix_feat_cont).mean()
    return distance


def style_loss(matrix_x, matrix_y):
    """
    Compute style loss between two torch.Tensor objects
    :params:
        matrix_x: torch.Tensor object
        matrix_y: torch.Tensor object
    :return:
        torch.Tensor object of style loss
    """

    def rgb_to_yuv(rgb):
        """
        Convert RGB to YUV color space
        :params:
            rgb: torch.Tensor object
        :return:
            torch.Tensor object of YUV color space
        """
        color_space_transformation_matrix = torch.Tensor(
            [
                [0.577350, 0.577350, 0.577350],
                [-0.577350, 0.788675, -0.211325],
                [-0.577350, -0.211325, 0.788675],
            ]
        ).to(rgb.device, non_blocking=True)
        yuv = torch.mm(color_space_transformation_matrix, rgb)
        return yuv

    shape = matrix_x.shape[1]

    if shape == 3:
        matrix_x = rgb_to_yuv(
            matrix_x.transpose(0, 1).contiguous().view(shape, -1)
        ).transpose(0, 1)
        matrix_y = rgb_to_yuv(
            matrix_y.transpose(0, 1).contiguous().view(shape, -1)
        ).transpose(0, 1)
    else:
        matrix_x = matrix_x.transpose(0, 1).contiguous().view(shape, -1).transpose(0, 1)
        matrix_y = matrix_y.transpose(0, 1).contiguous().view(shape, -1).transpose(0, 1)

    distance_matrix = distmat(matrix_x, matrix_y)

    if shape == 3:
        distance_matrix += distmat(matrix_x, matrix_y, cos_d=False)

    min_dist_1, _ = distance_matrix.min(1)
    min_dist_2, _ = distance_matrix.min(0)

    return torch.max(min_dist_1.mean(), min_dist_2.mean())


def moment_loss(matrix_x, matrix_y):
    """
    Compute moment loss between two torch.Tensor matrices
    :params:
        matrix_x: torch.Tensor matrix
        matrix_y: torch.Tensor matrix
    :return:
        torch.Tensor object of moment loss
    """
    loss = 0.0
    matrix_x = matrix_x.squeeze().t()
    matrix_y = matrix_y.squeeze().t()

    mean_x = matrix_x.mean(0, keepdim=True)
    mean_y = matrix_y.mean(0, keepdim=True)
    mean_difference = torch.abs(mean_x - mean_y).mean()

    loss = loss + mean_difference

    x_centered = matrix_x - mean_x
    y_centered = matrix_y - mean_y

    x_covariance = torch.mm(x_centered.t(), x_centered) / (x_centered.shape[0] - 1)
    y_covariance = torch.mm(y_centered.t(), y_centered) / (y_centered.shape[0] - 1)

    difference_covariance = torch.abs(x_covariance - y_covariance).mean()
    loss = loss + difference_covariance

    return loss


def sample_indices(feat_content):
    """
    Sample indices from feature map
    :params:
        feat_content: torch.Tensor object
    :return:
        channel_coords: np.array object of channel indices
    """
    const = 128**2  # 32k or so
    big_size = feat_content.shape[2] * feat_content.shape[3]  # num feaxels

    stride_x = int(max(math.floor(math.sqrt(big_size // const)), 1))
    offset_x = np.random.randint(stride_x)
    stride_y = int(max(math.ceil(math.sqrt(big_size // const)), 1))
    offset_y = np.random.randint(stride_y)
    channel_coords, spatial_coords = np.meshgrid(
        np.arange(feat_content.shape[2])[offset_x::stride_x],
        np.arange(feat_content.shape[3])[offset_y::stride_y],
    )

    channel_coords = channel_coords.flatten()
    spatial_coords = spatial_coords.flatten()
    return channel_coords, spatial_coords


def spatial_feature_extract(
    feature_results, feature_contents, offset_x_meshgrid, offset_y_meshgrid
):
    """
    Extract spatial features from feature maps
    :params:
        feature_results: list of torch.Tensor objects
        feature_contents: list of torch.Tensor objects
        offset_x_meshgrid: np.array object
        offset_y_meshgrid: np.array object
    :return:
        resampled_feature_results: list of torch.Tensor objects
    """
    resampled_feature_results, resampled_feature_content = [], []
    device = feature_results[0].device

    # for each extracted layer
    for index, (feat_res, feat_cont) in enumerate(
        zip(feature_results, feature_contents)
    ):
        feature_result = feat_res
        feature_content = feat_cont

        # hack to detect reduced scale
        if index > 0 and feature_results[index - 1].size(2) > feat_res.size(2):
            offset_x_meshgrid = offset_x_meshgrid / 2.0
            offset_y_meshgrid = offset_y_meshgrid / 2.0

        # go back to ints and get residual
        offset_x_floor = np.floor(offset_x_meshgrid).astype(np.float32)
        offset_x_residual = offset_x_meshgrid - offset_x_floor

        offset_y_floor = np.floor(offset_y_meshgrid).astype(np.float32)
        offset_y_residual = offset_y_meshgrid - offset_y_floor

        # do bilinear resample
        resample_weights = [
            torch.from_numpy((1.0 - offset_x_residual) * (1.0 - offset_y_residual))
            .float()
            .view(1, 1, -1, 1)
            .to(device, non_blocking=True),
            torch.from_numpy((1.0 - offset_x_residual) * offset_y_residual)
            .float()
            .view(1, 1, -1, 1)
            .to(device, non_blocking=True),
            torch.from_numpy(offset_x_residual * (1.0 - offset_y_residual))
            .float()
            .view(1, 1, -1, 1)
            .to(device, non_blocking=True),
            torch.from_numpy(offset_x_residual * offset_y_residual)
            .float()
            .view(1, 1, -1, 1)
            .to(device, non_blocking=True),
        ]

        offset_x_floor = np.clip(
            offset_x_floor.astype(np.int32), 0, feature_result.size(2) - 1
        )
        offset_y_floor = np.clip(
            offset_y_floor.astype(np.int32), 0, feature_result.size(3) - 1
        )

        resample_indices = [
            offset_x_floor * feature_result.size(3) + offset_y_floor,
            offset_x_floor * feature_result.size(3)
            + np.clip(offset_y_floor + 1, 0, feature_result.size(3) - 1),
            np.clip(offset_x_floor + 1, 0, feature_result.size(2) - 1)
            * feature_result.size(3)
            + offset_y_floor,
            np.clip(offset_x_floor + 1, 0, feature_result.size(2) - 1)
            * feature_result.size(3)
            + np.clip(offset_y_floor + 1, 0, feature_result.size(3) - 1),
        ]

        feature_result = feature_result.view(
            1,
            feature_result.size(1),
            feature_result.size(2) * feature_result.size(3),
            1,
        )
        feature_result = (
            feature_result[:, :, resample_indices[0], :]
            .mul_(resample_weights[0])
            .add_(
                feature_result[:, :, resample_indices[1], :].mul_(resample_weights[1])
            )
            .add_(
                feature_result[:, :, resample_indices[2], :].mul_(resample_weights[2])
            )
            .add_(
                feature_result[:, :, resample_indices[3], :].mul_(resample_weights[3])
            )
        )

        feature_content = feature_content.view(
            1,
            feature_content.size(1),
            feature_content.size(2) * feature_content.size(3),
            1,
        )
        feature_content = (
            feature_content[:, :, resample_indices[0], :]
            .mul_(resample_weights[0])
            .add_(
                feature_content[:, :, resample_indices[1], :].mul_(resample_weights[1])
            )
            .add_(
                feature_content[:, :, resample_indices[2], :].mul_(resample_weights[2])
            )
            .add_(
                feature_content[:, :, resample_indices[3], :].mul_(resample_weights[3])
            )
        )

        resampled_feature_results.append(feature_result)
        resampled_feature_content.append(feature_content)

    concatenated_feature_results = torch.cat(
        [li.contiguous() for li in resampled_feature_results], 1
    )
    concatenated_feature_content = torch.cat(
        [li.contiguous() for li in resampled_feature_content], 1
    )

    offset_x_meshgrid = (
        torch.from_numpy(offset_x_meshgrid)
        .view(1, 1, concatenated_feature_results.size(2), 1)
        .float()
        .to(device, non_blocking=True)
    )
    offset_y_meshgrid = (
        torch.from_numpy(offset_y_meshgrid)
        .view(1, 1, concatenated_feature_results.size(2), 1)
        .float()
        .to(device, non_blocking=True)
    )

    concatenated_feature_results = torch.cat(
        [concatenated_feature_results, offset_x_meshgrid, offset_y_meshgrid], 1
    )
    concatenated_feature_content = torch.cat(
        [concatenated_feature_content, offset_x_meshgrid, offset_y_meshgrid], 1
    )
    return concatenated_feature_results, concatenated_feature_content


def calculate_loss(feat_result, feat_content, feat_style, indices, content_weight):
    """
    Calculate the loss between the result and the content and style images.
    :params:
        feat_result: the feature map of the result image
        feat_content: the feature map of the content image
        feat_style: the feature map of the style image
        indices: the indices of the style image
        content_weight: the weight of the content loss
    :return:
        loss: the loss between the result and the content and style images
    """
    # spatial feature extract
    num_locations = 1024
    spatial_result, spatial_content = spatial_feature_extract(
        feat_result,
        feat_content,
        indices[0][:num_locations],
        indices[1][:num_locations],
    )
    loss_content = content_loss(spatial_result, spatial_content)

    shape = feat_style.shape[1]
    spatial_style = feat_style.view(1, shape, -1, 1)
    feat_max = (
        3 + 2 * 64 + 128 * 2 + 256 * 3 + 512 * 2
    )  # (sum of all extracted channels)

    loss_remd = style_loss(
        spatial_result[:, :feat_max, :, :], spatial_style[:, :feat_max, :, :]
    )

    loss_moment = moment_loss(spatial_result[:, :-2, :, :], spatial_style)
    # palette matching
    content_weight_frac = 1.0 / max(content_weight, 1.0)
    loss_moment += content_weight_frac * style_loss(
        spatial_result[:, :3, :, :], spatial_style[:, :3, :, :]
    )

    loss_style = loss_remd + 1.0 * loss_moment
    # print(f'Style: {loss_style.item():.3f}, Content: {loss_content.item():.3f}')

    style_weight = 1.0 + 1.0
    loss_total = (content_weight * loss_content + loss_style) / (
        content_weight + style_weight
    )
    return loss_total
