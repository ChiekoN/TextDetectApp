import cv2
import pytesseract
import numpy as np
import os
from PIL import Image

from textdetect import lanms, locality_aware_nms

input_size = 512

def restore_rectangle_rbox(origin, geometry):
    """ Taken from icdar.py in the original EAST module."""

    d = geometry[:, :4]
    angle = geometry[:, 4]
    # for angle > 0
    origin_0 = origin[angle >= 0]
    d_0 = d[angle >= 0]
    angle_0 = angle[angle >= 0]
    if origin_0.shape[0] > 0:
        p = np.array([np.zeros(d_0.shape[0]), -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3], -d_0[:, 0] - d_0[:, 2],
                      d_0[:, 1] + d_0[:, 3], np.zeros(d_0.shape[0]),
                      np.zeros(d_0.shape[0]), np.zeros(d_0.shape[0]),
                      d_0[:, 3], -d_0[:, 2]])
        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = np.array([np.cos(angle_0), np.sin(angle_0)]).transpose((1, 0))
        rotate_matrix_x = np.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = np.array([-np.sin(angle_0), np.cos(angle_0)]).transpose((1, 0))
        rotate_matrix_y = np.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = np.sum(rotate_matrix_x * p, axis=2)[:, :, np.newaxis]  # N*5*1
        p_rotate_y = np.sum(rotate_matrix_y * p, axis=2)[:, :, np.newaxis]  # N*5*1

        p_rotate = np.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_0 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_0 = np.concatenate([new_p0[:, np.newaxis, :], new_p1[:, np.newaxis, :],
                                  new_p2[:, np.newaxis, :], new_p3[:, np.newaxis, :]], axis=1)  # N*4*2
    else:
        new_p_0 = np.zeros((0, 4, 2))
    # for angle < 0
    origin_1 = origin[angle < 0]
    d_1 = d[angle < 0]
    angle_1 = angle[angle < 0]
    if origin_1.shape[0] > 0:
        p = np.array([-d_1[:, 1] - d_1[:, 3], -d_1[:, 0] - d_1[:, 2],
                      np.zeros(d_1.shape[0]), -d_1[:, 0] - d_1[:, 2],
                      np.zeros(d_1.shape[0]), np.zeros(d_1.shape[0]),
                      -d_1[:, 1] - d_1[:, 3], np.zeros(d_1.shape[0]),
                      -d_1[:, 1], -d_1[:, 2]])
        p = p.transpose((1, 0)).reshape((-1, 5, 2))  # N*5*2

        rotate_matrix_x = np.array([np.cos(-angle_1), -np.sin(-angle_1)]).transpose((1, 0))
        rotate_matrix_x = np.repeat(rotate_matrix_x, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))  # N*5*2

        rotate_matrix_y = np.array([np.sin(-angle_1), np.cos(-angle_1)]).transpose((1, 0))
        rotate_matrix_y = np.repeat(rotate_matrix_y, 5, axis=1).reshape(-1, 2, 5).transpose((0, 2, 1))

        p_rotate_x = np.sum(rotate_matrix_x * p, axis=2)[:, :, np.newaxis]  # N*5*1
        p_rotate_y = np.sum(rotate_matrix_y * p, axis=2)[:, :, np.newaxis]  # N*5*1

        p_rotate = np.concatenate([p_rotate_x, p_rotate_y], axis=2)  # N*5*2

        p3_in_origin = origin_1 - p_rotate[:, 4, :]
        new_p0 = p_rotate[:, 0, :] + p3_in_origin  # N*2
        new_p1 = p_rotate[:, 1, :] + p3_in_origin
        new_p2 = p_rotate[:, 2, :] + p3_in_origin
        new_p3 = p_rotate[:, 3, :] + p3_in_origin

        new_p_1 = np.concatenate([new_p0[:, np.newaxis, :], new_p1[:, np.newaxis, :],
                                  new_p2[:, np.newaxis, :], new_p3[:, np.newaxis, :]], axis=1)  # N*4*2
    else:
        new_p_1 = np.zeros((0, 4, 2))
    return np.concatenate([new_p_0, new_p_1])


def restore_rectangle(origin, geometry):
    """ Taken from icdar.py in the original EAST module."""
    return restore_rectangle_rbox(origin, geometry)


def decode_prediction(scores, geometry, score_th=0.1):
    """ Extract detections which have higher scores than threshold,
        and return bounding box coordinates with score.
    """  

    scores = np.squeeze(scores) # 128*128
    geometry = np.squeeze(geometry, axis=0) # 5*128*128

    save_index = np.argwhere(scores > score_th) # shape(N,2)
    geo_reshaped = geometry[:, save_index[:, 0], save_index[:, 1]].T

    # origin should be (x, y) => index is multiplied by 4
    coordinates = restore_rectangle(save_index[:, ::-1]*4, geo_reshaped)


    #v_r = coordinates.reshape(-1, 8).T
    v_r = coordinates.reshape(-1, 8)
    v_c = np.array(scores[save_index[:, 0], save_index[:, 1]]).reshape(-1, 1)
    boxes = np.vstack((v_r.T, v_c.T)).T

    return boxes


def adjust_boxes_to_image(boxes, ratioW, ratioH, origW, origH, margin=0.0):
    """ Rescale the boxes to match them with original image size.
        margin (ratio): Add some margin to boxes to crop the area a bit larger
    """




def padding_edges(cropped, pad):
    """ Add padding to a perimeter of cropped with the colour of edge pixels.
        return : padded image
    """

    # Get the average color of edge pixels
    left = cropped[:, 0, :]
    right = cropped[:, -1, :]
    top = cropped[0, :, :]
    bottom = cropped[-1, :, :]

    all = np.vstack((left, right, top, bottom))
    rgb = np.sum(all, axis=0) / all.shape[0]
    rgb = rgb.astype(int)

    new_img = np.ones((cropped.shape[0] + pad + pad, cropped.shape[1] + pad + pad, cropped.shape[2])) * rgb
    new_img = new_img.astype(int)

    new_img[pad:(pad+cropped.shape[0]), pad:(pad+cropped.shape[1]), :] = cropped
    return new_img


def text_detect(imagebytes):

    im_nparr = np.fromstring(imagebytes, np.uint8)
    image_mat = cv2.imdecode(im_nparr, cv2.IMREAD_COLOR)

    # os.environ['DISPLAY'] = 'localhost:10.0'
    # cv2.namedWindow('Canvas')
    # cv2.imshow('Canvas', image_mat)
    # cv2.waitKey(0)
    # cv2.destroyWindow('Canvas')
    # print("End")

    (origH, origW) = image_mat.shape[:2]

    # ratio to be used to scale bounding boxes for the result
    ratioH = origH / float(input_size)
    ratioW = origW / float(input_size)
    print("ratioH, ratioW = {}, {}\n".format(ratioH, ratioW))

    image = cv2.resize(image_mat, (input_size, input_size))
    (H, W) = image.shape[:2]

    
    #
    # EAST detector with OpenCV
    #

    # Load model file
    py_path = os.path.dirname(os.path.abspath(__file__))
    abspath_pb = py_path + "/" + "model/frozen_east_text_detection.pb"
    net = cv2.dnn.readNet(abspath_pb)

    #blobFromImage(image, scalefactor, (size), (mean for RGB)), swapRB, crop)
    blob = cv2.dnn.blobFromImage(image, 1.0, (H, W), (123.68, 116.78, 103.94), swapRB=True, crop=False)

    net.setInput(blob)
    layerNames = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]
    (scores, geometry) = net.forward(layerNames)

    print("scores.shape= {}".format(scores.shape))
    print("geometry.shape = {}".format(geometry.shape))
    # scores.shape = (1, 1, 128, 128)
    # geometry.shape = (1, 5, 128, 128)  top, right, bottom, left, angle

    # Get boxes from scores and geometry
    # boxes.shape = (<num_samples>, 9)
    #  9: coordinates of four corners, and score
    boxes = decode_prediction(scores, geometry, 0.1)
 
    #
    # Locally Aware NMS ---- from the original source code
    #
    # !!! CAN'T CALL THIS on windows (because can't compile and make adaptor.so object on Windows)
    boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), 0.4)

    # In the case of the use on windows, TODO: comment out above line and uncomment the following line.
    #boxes = locality_aware_nms.nms_locality(boxes.astype(np.float64), 0.4)

    print("boxes.len = {}".format(boxes.shape[0]))
    if(boxes.shape[0]):
        print("conf after nms = {}".format(boxes[:, 8]))

        box_thresh = 0.1
        # here we filter some low score boxes by the average score map, this is different from the orginal paper
        score_map = scores.squeeze()
        for i, box in enumerate(boxes):
            mask = np.zeros_like(score_map, dtype=np.uint8)
            cv2.fillPoly(mask, box[:8].reshape((-1, 4, 2)).astype(np.int32) // 4, 1)
            boxes[i, 8] = cv2.mean(score_map, mask)[0] # Because of LANMS
        boxes = boxes[boxes[:, 8] > box_thresh]

        # Rescale the bounding boxes so they fit the original image size.
        margin = .0
        final_conf = boxes[:, 8]
        #print("conf={}".format(final_conf))
        final_boxes = boxes[:, 0:8]
        final_boxes = final_boxes.reshape(-1, 4, 2)
        final_boxes[:, :, 0] = final_boxes[:, :, 0] * ratioW # rescale X to the original image
        final_boxes[:, :, 1] = final_boxes[:, :, 1] * ratioH # rescale Y to the original image

        for (XY1, XY2, XY3, XY4) in final_boxes:
            print("{}, {}, {}, {}, {}, {}, {}, {}".format(XY1[0], XY1[1], XY2[0], XY2[1], XY3[0], XY3[1], XY4[0], XY4[1]))

        final_boxes = final_boxes.astype(int)


        # When the quadrilateral is skewed, take the outermost points to get a rectangle
        startX = np.minimum(final_boxes[:, 0, 0], final_boxes[:, 3, 0])
        startY = np.minimum(final_boxes[:, 0, 1], final_boxes[:, 1, 1])
        endX = np.maximum(final_boxes[:, 1, 0], final_boxes[:, 2, 0])
        endY = np.maximum(final_boxes[:, 2, 1], final_boxes[:, 3, 1])

        # padding by ratio
        margin_X = (endX - startX) * margin
        margin_Y = (endY - startY) * margin
        startX = np.maximum(startX - margin_X.astype(int), 0)
        startY = np.maximum(startY - margin_Y.astype(int), 0)
        endX = np.minimum(endX + margin_X.astype(int), origW)
        endY = np.minimum(endY + margin_Y.astype(int), origH)

        box_num = final_conf.shape[0]

    else:
        box_num = 0

    #
    # Tesseract OCR
    #
    os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'
    
    t_config = "-l eng --psm 7"
    #t_config = "-l eng+jpn --psm 6 --oem 1 --user-words tess_dict/eng.user-words"
    # Japanese cant't be encoded sometimes on Windows.
    # To avoid it, set PYTHONIOENCODING=UTF-8.
    # To use tesseract language data, set TESSDATA_PREFIX="C:\Program Files\Tesseract-OCR"

    outtext_list = []
    for i in np.arange(box_num):
        output_text = image_mat[startY[i]:endY[i], startX[i]:endX[i]]
        # padding all edges with the background colour
        output_text_pad = np.asarray(padding_edges(output_text, 3))

        #if i == 0:
        #       #cv2.imwrite("aaa.png", output[startY[i]:endY[i], startX[i]:endX[i]])
        #       cv2.imwrite("aaa.png", output_text_pad)
        #       break

        text = pytesseract.image_to_string(np.uint8(output_text_pad), config=t_config)
        cv2.polylines(image_mat, [final_boxes[i]], True, (0, 0, 255), 2)
        print("{} : {} ({})".format(i, text, final_conf[i]), flush=True)
        text_info = {}
        text_info['conf'] = final_conf[i]
        text_info['text'] = text
        outtext_list.append(text_info)
        cv2.putText(image_mat, str(i), (startX[i], startY[i]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imwrite("textdetect_output.png", image_mat)
    outtext_list.sort(key=lambda ol: ol['conf'], reverse=True)

    return outtext_list