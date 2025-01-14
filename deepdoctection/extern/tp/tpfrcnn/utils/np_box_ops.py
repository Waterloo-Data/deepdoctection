# -*- coding: utf-8 -*-
# File: box_ops.py

# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""
Operations for [N, 4] numpy arrays representing bounding boxes.

Example box operations that are supported:

-  Areas: compute bounding box areas

-  IOU: pairwise intersection-over-union scores
"""

import numpy as np


def area(boxes):
    """
    Computes area of boxes.

    :param boxes: Numpy array with shape [N, 4] holding N boxes

    :return: A numpy array with shape [N*1] representing box areas
    """
    return (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])


def intersection(boxes1, boxes2):
    """
    Compute pairwise intersection areas between boxes.

    :param boxes1: a numpy array with shape [N, 4] holding N boxes
    :param boxes2: a numpy array with shape [M, 4] holding M boxes

    :return: A numpy array with shape [N*M] representing pairwise intersection area
    """

    [y_min1, x_min1, y_max1, x_max1] = np.split(boxes1, 4, axis=1)  # pylint: disable=W0632
    [y_min2, x_min2, y_max2, x_max2] = np.split(boxes2, 4, axis=1)  # pylint: disable=W0632

    all_pairs_min_ymax = np.minimum(y_max1, np.transpose(y_max2))
    all_pairs_max_ymin = np.maximum(y_min1, np.transpose(y_min2))
    intersect_heights = np.maximum(
        np.zeros(all_pairs_max_ymin.shape, dtype="f4"), all_pairs_min_ymax - all_pairs_max_ymin
    )
    all_pairs_min_xmax = np.minimum(x_max1, np.transpose(x_max2))
    all_pairs_max_xmin = np.maximum(x_min1, np.transpose(x_min2))
    intersect_widths = np.maximum(
        np.zeros(all_pairs_max_xmin.shape, dtype="f4"), all_pairs_min_xmax - all_pairs_max_xmin
    )
    return intersect_heights * intersect_widths


def iou(boxes1, boxes2):
    """
    Computes pairwise intersection-over-union between box collections.

    :param boxes1: a numpy array with shape [N, 4] holding N boxes.
    :param boxes2: a numpy array with shape [M, 4] holding M boxes.

    :return: A numpy array with shape [N, M] representing pairwise iou scores.
    """

    intersect = intersection(boxes1, boxes2)
    area1 = area(boxes1)
    area2 = area(boxes2)
    union = np.expand_dims(area1, axis=1) + np.expand_dims(area2, axis=0) - intersect
    return intersect / union


def ioa(boxes1, boxes2):
    """
    Computes pairwise intersection-over-area between box collections.

    Intersection-over-area (ioa) between two boxes box1 and box2 is defined as
    their intersection area over box2's area. Note that ioa is not symmetric,
    that is, IOA(box1, box2) != IOA(box2, box1).

    :param boxes1: a numpy array with shape [N, 4] holding N boxes.
    :param boxes2: a numpy array with shape [M, 4] holding N boxes.

    :return: A numpy array with shape [N, M] representing pairwise ioa scores.
    """

    intersect = intersection(boxes1, boxes2)
    inv_areas = np.expand_dims(1.0 / area(boxes2), axis=0)
    return intersect * inv_areas


# Malisiewicz et al.
def non_max_suppression(boxes, overlap_thresh):
    """
    Simple nms without using score picking boxes. Will

    :param boxes: [N, 4] numpy arrays representing bounding boxes [x1,y1,x2,y2]
    :param overlap_thresh: overlap threshold.
    """
    if len(boxes) == 0:
        return []

    pick = []

    x_1 = boxes[:, 0]
    y_1 = boxes[:, 1]
    x_2 = boxes[:, 2]
    y_2 = boxes[:, 3]

    area = (x_2 - x_1 + 1) * (y_2 - y_1 + 1)  # pylint: disable=W0621
    idxs = np.argsort(y_2)

    while len(idxs) > 0:

        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)
        xx1 = np.maximum(x_1[i], x_1[idxs[:last]])
        yy1 = np.maximum(y_1[i], y_1[idxs[:last]])
        xx2 = np.minimum(x_2[i], x_2[idxs[:last]])
        yy2 = np.minimum(y_2[i], y_2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))
    return pick
