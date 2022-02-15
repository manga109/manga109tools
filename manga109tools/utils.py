import numpy as np


def bbox_contain(bbox_a: tuple, bbox_b: tuple) -> bool:
    """Calculate whether bbox_a contains bbox_b or not.
    Each bounding box comparises four integers -- (xmin, ymin, xmax, ymax).

    Args:
        bbox_a (tuple): a bounding box
        bbox_b (tuple): another bounding box

    Returns:
        bool:
        whether bbox_a contains bbox_b or not
    """
    xmin_a, ymin_a, xmax_a, ymax_a = bbox_a
    xmin_b, ymin_b, xmax_b, ymax_b = bbox_b
    if not (ymin_a <= ymin_b and ymax_b <= ymax_a):
        return False

    if not (xmin_a <= xmin_b and xmax_b <= xmax_a):
        return False

    return True


def bboxes_iou(bboxes_a: np.ndarray, bboxes_b: np.ndarray):
    """Calculate the Intersection of Unions (IoUs) between bounding boxes.
    IoU is calculated as a ratio of area of the intersection
    and area of the union.
    This function accepts both :obj:`numpy.ndarray` as inputs.
    Please note that both :obj:`bboxes_a` and :obj:`bboxes_b` need to be same type.
    The output is same type as the type of the inputs.
    Args:
        bboxes_a (numpy.ndarray): An array whose shape is :math:`(N, 4)`.
            :math:`N` is the number of bounding boxes.
        bboxes_b (numpy.ndarray): An array similar to :obj:`bboxes_a`,
            whose shape is :math:`(K, 4)`.
    Returns:
        numpy.ndarray:
        An array whose shape is :math:`(N, K)`. \
        An element at index :math:`(n, k)` contains IoUs between \
        :math:`n` th bounding box in :obj:`bboxes_a` and :math:`k` th bounding \
        box in :obj:`bboxes_b`.

    This function is modified from
    https://github.com/chainer/chainercv/blob/master/chainercv/utils/bbox/bbox_iou.py
    The MIT License
    Copyright (c) 2017 Preferred Networks, Inc.
    """
    if bboxes_a.shape[1] != 4 or bboxes_b.shape[1] != 4:
        raise IndexError

    # top left
    tl = np.maximum(bboxes_a[:, None, :2], bboxes_b[:, :2])
    # bottom right
    br = np.minimum(bboxes_a[:, None, 2:], bboxes_b[:, 2:])

    area_i = np.prod(br - tl, axis=2) * (tl < br).all(axis=2)
    area_a = np.prod(bboxes_a[:, 2:] - bboxes_a[:, :2], axis=1)
    area_b = np.prod(bboxes_b[:, 2:] - bboxes_b[:, :2], axis=1)
    return area_i / (area_a[:, None] + area_b - area_i)


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except Exception:
        return False


def is_hexadecimal(value: str) -> bool:
    try:
        int(value, 16)
        return True
    except Exception:
        return False
