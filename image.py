import cv2
import base64
import numpy as np

# Helper function to encode an image for display in Dash
def encode_image_for_display(image):
    _, buffer = cv2.imencode('.png', image)
    encoded = base64.b64encode(buffer).decode('utf-8')
    return encoded

def processing_image(content, filename, blur_level, median_blur, bw_threshold, ecc_threshold, lo_area_threshold, hi_area_threshold, final_points):
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    image = np.asarray(bytearray(decoded), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    height, width = image.shape[:2]
    #cv2.rectangle(image,(0,0),(width-1,height-1),(0,255,0),1)
    #cv2.rectangle(image,(0,0),(width-1,height-1),(0,58,168),1)

    # Original image for display
    #original_image_encoded = encode_image_for_display(image)

    # Apply Gaussian blur
    if len(median_blur)==0:
        blurred = cv2.GaussianBlur(image, (blur_level,blur_level) if blur_level % 2 != 0 else (blur_level + 1,blur_level + 1), 0)
    # Apply median blur
    else: 
        blurred = cv2.medianBlur(image, blur_level if blur_level % 2 != 0 else blur_level + 1)
    cv2.rectangle(blurred,(0,0),(width-1,height-1),(0,94,199),1)
    blurred_image_encoded = encode_image_for_display(blurred)

    # Convert to grayscale and apply binary threshold
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, bw_threshold, 255, cv2.THRESH_BINARY)
    threshold_image_encoded = encode_image_for_display(thresh)

    # Find contours and filter by area
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > lo_area_threshold and cv2.contourArea(cnt) < hi_area_threshold]

    # Draw the centers of the triangles
    for cnt in large_contours:
        M = cv2.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            # Calculate central moments
            mu20 = M['mu20'] / M['m00']
            mu02 = M['mu02'] / M['m00']
            mu11 = M['mu11'] / M['m00']
            
            # Calculate major and minor axis
            common_term = np.sqrt((mu20 - mu02)**2 + 4*mu11**2)
            major_axis = np.sqrt(2) * np.sqrt(mu20 + mu02 + common_term)
            minor_axis = np.sqrt(2) * np.sqrt(mu20 + mu02 - common_term)
            
            # Calculate eccentricity
            eccentricity = np.sqrt(1 - (minor_axis**2 / major_axis**2))
            if eccentricity <= ecc_threshold:
                final_points.append((filename, cx, cy))
                #cv2.circle(image, (cx, cy), 2, (0, 255*eccentricity*1.5, 0), -1)
                cv2.circle(image, (cx, cy), 2, (0, 255, 0), -1)

    final_image_encoded = encode_image_for_display(image)

    return blurred_image_encoded, threshold_image_encoded, final_image_encoded
