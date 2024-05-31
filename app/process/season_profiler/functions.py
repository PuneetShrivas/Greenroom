import cv2
import numpy as np
from core.common_modules.image_tools import encode_image, resize_image
import os
import tempfile
from fastapi import HTTPException

def detect_undertones(image): #works okay
    # Load the pre-trained face detector from OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert the image to grayscale for face detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30))
    
    # If no face is detected, return 'Neutral'
    if len(faces) == 0:
        return 'Neutral'
    
    # Take the first detected face
    (x, y, w, h) = faces[0]
    
    # Draw a bounding box around the detected face
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Extract the face region
    face_region = image[y:y+h, x:x+w]
    
    # Convert the face region to the LAB color space
    lab_face_region = cv2.cvtColor(face_region, cv2.COLOR_BGR2LAB)
    
    # Calculate the average 'L', 'a', and 'b' values of the LAB face region
    avg_l_value = np.mean(lab_face_region[:, :, 0])
    avg_a_value = np.mean(lab_face_region[:, :, 1])
    avg_b_value = np.mean(lab_face_region[:, :, 2])
    
    # Calculate the normalized 'a', 'b', and 'L' values
    norm_a_value = avg_a_value / np.mean(lab_face_region)
    norm_b_value = avg_b_value / np.mean(lab_face_region)
    norm_l_value = avg_l_value / np.mean(lab_face_region)
    
    # Check if the absolute difference between average of 'a' and 'b' is less than 10.5
    if abs(avg_a_value - avg_b_value) < 10.5:
        skin_undertone = 'Neutral'
    else:
        # Check if b' - a' is less than 0.08 to determine undertone
        if norm_b_value - norm_a_value < 0.08:
            skin_undertone = 'Cool'
        else:
            skin_undertone = 'Warm'
    
    # # Write the normalized 'a', 'b', and 'L' values and the skin tone on the image
    # cv2.putText(image, f"Normalized 'a' Value: {norm_a_value:.2f}", (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # cv2.putText(image, f"Normalized 'b' Value: {norm_b_value:.2f}", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # cv2.putText(image, f"Normalized 'L' Value: {norm_l_value:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    # cv2.putText(image, f"Skin Undertone: {skin_undertone}", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return skin_undertone

def detect_iris_color(image):
    # Load the pre-trained face and eye detectors from OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    # Convert the image to grayscale for face detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # If no face is detected, return None
    if len(faces) == 0:
        print("Error: Unable to detect face for iris color")
        return None
    
    # Take the first detected face
    (x_face, y_face, w_face, h_face) = faces[0]
    
    # Draw a bounding box around the detected face
    cv2.rectangle(image, (x_face, y_face), (x_face + w_face, y_face + h_face), (0, 255, 0), 2)
    
    # Convert the face region to grayscale for eye detection
    gray_face = gray_image[y_face:y_face+h_face, x_face:x_face+w_face]
    
    # Detect eyes in the face region
    eyes = eye_cascade.detectMultiScale(gray_face, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
    
    # If less than two eyes are detected, return None
    if len(eyes) < 2:
        print("Error: Unable to detect both eyes.", len(eyes))
        return None
    
    # Initialize lists to store iris pixel colors and eye bounding box coordinates
    iris_colors = []
    eye_boxes = []
    
    # Loop through each detected eye region
    for (x_eye, y_eye, w_eye, h_eye) in eyes:
        # Convert eye coordinates to global image coordinates
        x_eye_global = x_face + x_eye
        y_eye_global = y_face + y_eye
        
        # Define the region of interest for the iris (assuming it occupies the center portion)
        iris_x = x_eye_global + w_eye//4
        iris_y = y_eye_global + h_eye//4
        iris_width = w_eye//2
        iris_height = h_eye//2
        
        # Extract the region of interest (ROI) corresponding to the iris
        iris_roi = image[iris_y:iris_y + iris_height, iris_x:iris_x + iris_width]
        
        # Convert the ROI to HSV color space
        hsv_roi = cv2.cvtColor(iris_roi, cv2.COLOR_BGR2HSV)
        
        # Define stricter color thresholds for blue, dark brown, light brown, gray, and green
        blue_lower = np.array([90, 50, 50])
        blue_upper = np.array([130, 255, 255])
        dark_brown_lower = np.array([10, 50, 50])
        dark_brown_upper = np.array([15, 255, 255])
        light_brown_lower = np.array([16, 50, 50])
        light_brown_upper = np.array([20, 255, 255])
        gray_lower = np.array([0, 0, 80])
        gray_upper = np.array([180, 30, 220])
        green_lower = np.array([30, 50, 50])
        green_upper = np.array([90, 255, 255])
        
        # Threshold the HSV image to extract blue, dark brown, light brown, gray, and green regions
        blue_mask = cv2.inRange(hsv_roi, blue_lower, blue_upper)
        dark_brown_mask = cv2.inRange(hsv_roi, dark_brown_lower, dark_brown_upper)
        light_brown_mask = cv2.inRange(hsv_roi, light_brown_lower, light_brown_upper)
        gray_mask = cv2.inRange(hsv_roi, gray_lower, gray_upper)
        green_mask = cv2.inRange(hsv_roi, green_lower, green_upper)
        
        # Count the number of non-zero pixels in each mask
        blue_count = cv2.countNonZero(blue_mask)
        dark_brown_count = cv2.countNonZero(dark_brown_mask)
        light_brown_count = cv2.countNonZero(light_brown_mask)
        gray_count = cv2.countNonZero(gray_mask)
        green_count = cv2.countNonZero(green_mask)
        
        # Classify the iris color based on the counts
        if blue_count > dark_brown_count and blue_count > light_brown_count and blue_count > gray_count and blue_count > green_count:
            iris_color = "blue"
        elif dark_brown_count > blue_count and dark_brown_count > light_brown_count and dark_brown_count > gray_count and dark_brown_count > green_count:
            iris_color = "dark brown"
        elif light_brown_count > blue_count and light_brown_count > dark_brown_count and light_brown_count > gray_count and light_brown_count > green_count:
            iris_color = "light brown"
        elif gray_count > blue_count and gray_count > dark_brown_count and gray_count > light_brown_count and gray_count > green_count:
            iris_color = "gray"
        elif green_count > blue_count and green_count > dark_brown_count and green_count > light_brown_count and green_count > gray_count:
            iris_color = "green"
        else:
            iris_color = "black"  # Default to black if none of the above conditions are met
        
        # Append the iris color to the list
        iris_colors.append(iris_color)
        
        # Store the eye bounding box coordinates
        eye_boxes.append((x_eye_global, y_eye_global, w_eye, h_eye))
    
    # # Draw bounding boxes around the detected eyes and label the iris color
    # for (x_eye, y_eye, w_eye, h_eye), iris_color in zip(eye_boxes, iris_colors):
    #     # Convert the iris color to tuple format for displaying
    #     iris_color_display = (0, 0, 255) if iris_color == "black" else (255, 255, 255)
        
    #     # Draw bounding box around the iris region
    #     cv2.rectangle(image, (iris_x, iris_y), (iris_x + iris_width, iris_y + iris_height), iris_color_display, 2)
        
    #     # Display the iris color label
    #     cv2.putText(image, f"Iris Color: {iris_color}", (x_eye, y_eye - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, iris_color_display, 2)
    
    return iris_colors[0]

def detect_hair_color(image):
    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Load pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Define predefined hair colors in BGR format
    hair_colors = {
        'black': np.array([0, 0, 0]),
        'brown_black': np.array([76, 85, 90]),  # Updated color definition for brown black
        'brown': np.array([50, 50, 50]),
        'blonde': np.array([255, 200, 150]),
        'gray': np.array([180, 180, 180]),
        'red': np.array([0, 0, 255])
    }

    # Detect faces
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=8, minSize=(30, 30))

    # Initialize variables for hair region bounding box
    hair_left = 0
    hair_top = 0
    hair_width = 0
    hair_height = 0

    # Define proportion of face width and height to use for hair region
    hair_width_ratio = 0.5
    hair_height_ratio = 0.25

    # Loop over detected faces
    for (x, y, w, h) in faces:
        # Calculate hair region bounding box
        hair_width = int(w * hair_width_ratio)
        hair_height = int(h * hair_height_ratio)
        hair_left = x + (w - hair_width) // 2
        hair_top = y - int(h * 0.25)  # Adjust the hair region vertically
        
        # Dilate and erode the hair region to clean up the mask
        hair_mask = np.zeros_like(hsv_image[:, :, 0], dtype=np.uint8)
        hair_mask[hair_top:hair_top + hair_height, hair_left:hair_left + hair_width] = 255
        hair_mask = cv2.dilate(hair_mask, None, iterations=2)
        hair_mask = cv2.erode(hair_mask, None, iterations=3)

        # Ensure that the mask has the same number of channels as the image
        hair_mask = cv2.merge([hair_mask] * 3)

        # Apply the hair mask to the HSV image to extract the hair region
        hair_region_hsv = cv2.bitwise_and(hsv_image, hair_mask)

        # Convert the hair region back to BGR color space
        hair_region = cv2.cvtColor(hair_region_hsv, cv2.COLOR_HSV2BGR)

        # # Display the hair region and hair mask for visualization
        # cv2.imshow('Dilated and Eroded Hair Region', hair_region)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Calculate the average color of the hair region
        average_color = cv2.mean(hair_region)[:3]

        # Assign the closest color category to the average color
        closest_color = None
        min_distance = float('inf')
        for color, color_value in hair_colors.items():
            distance = np.linalg.norm(average_color - color_value)
            if distance < min_distance:
                min_distance = distance
                closest_color = color
                return closest_color
    return None

def detect_skin_color(image):
    # Load the face cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        return None  # No faces detected
    
    # Select the largest face as the region of interest (ROI)
    largest_face = max(faces, key=lambda face: face[2] * face[3])
    x, y, w, h = largest_face
    
    # Define a smaller portion of the face rectangle as the refined ROI
    roi_margin = 0.2  # Margin to leave around the face rectangle
    roi_x = int(x + roi_margin * w)
    roi_y = int(y + roi_margin * h)
    roi_w = int(w * (1 - 2 * roi_margin))
    roi_h = int(h * (1 - 2 * roi_margin))
    
    face_roi = image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    
    # Calculate the average BGR color of the skin region
    average_bgr_color = np.mean(face_roi, axis=(0, 1))
    print(average_bgr_color)
    
    # Define color ranges for each category (in BGR format)
    color_ranges = {
        "Fair": (177, 204, 234),   # Light beige to pale pink
        "White": (205, 216, 228),  # Off-white to cream
        "Golden": (131, 180, 207), # Warm beige to honey
        "Brown": (73, 148, 123),   # Tan to cocoa
        "Beige": (137, 185, 186),  # Medium beige to taupe
        "Dark Brown": (53, 102, 90) # Deep brown to mahogany
    }
    
    # Calculate the closest color based on Euclidean distance
    closest_color = None
    min_distance = float('inf')
    for category, target_color in color_ranges.items():
        distance = np.linalg.norm(average_bgr_color - target_color)
        if distance < min_distance:
            min_distance = distance
            closest_color = category
    
    return closest_color

def softmax(x): #works okay
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

    # Load pre-trained Caffe models for gender and age detection
    gender_net = cv2.dnn.readNetFromCaffe('data/deploy_age.prototxt','data/age_net.caffemodel'
		)
    age_net = cv2.dnn.readNetFromCaffe('data/deploy_gender.prototxt','data/gender_net.caffemodel'
		)    
    # Load pre-trained Haar cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
   # Detect faces in the image
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    age_list = ['(0, 2)', '(4, 6)', '(8, 12)', '(15, 20)', '(25, 32)', '(38, 43)', '(48, 53)', '(60, 100)']
    gender_list = ['Male', 'Female']
    
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)

        # Get Face 
        face_img = image[y:y+h, x:x+w].copy()
        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        blob = cv2.dnn.blobFromImage(face_img, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

        # Predict Gender
        gender_net.setInput(blob)
        gender_preds = gender_net.forward()
        gender_softmax = softmax(gender_preds[0])
        gender_index = np.argmax(gender_softmax)
        gender = gender_list[gender_index]
        gender_accuracy = gender_softmax[gender_index] * 100
        print("Gender: {}, Accuracy: {:.2f}%".format(gender, gender_accuracy))

        # Predict Age
        age_net.setInput(blob)
        age_preds = age_net.forward()
        age_softmax = softmax(age_preds[0])
        age_index = np.argmax(age_softmax)
        age_range = age_list[age_index]
        age_accuracy = age_softmax[age_index] * 100
        print("Age Range: {}, Accuracy: {:.2f}%".format(age_range, age_accuracy))

        # Draw text for gender and age prediction
        cv2.putText(image, "Gender: {}, Accuracy: {:.2f}%".format(gender, gender_accuracy), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(image, "Age Range: {}, Accuracy: {:.2f}%".format(age_range, age_accuracy), (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    # Display the image with predictions
    cv2.imshow("Gender and Age Detection", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return gender, age_range

def define_season(undertone, iris_color, hair_color, skin_color):
    # Define the rules for each season based on undertone, iris color, and hair color
    seasons = {
    "Clear Spring": ("warm", {"blue", "green", "light_brown"}, {"blonde", "brown","brown_black"},{"fair","white","golden"}),#B
    "Warm Spring": ("warm", {"brown", "light_brown", "green",}, {"brown", "blonde", "red"},{"fair","golden","beige","brown"}),#B
    "Clear Winter": ("cool", {"blue", "green", "gray"}, {"black", "brown", "brown_black"},{"fair","white","golden","brown","beige","dark_brown"}),#B
    "Warm Autumn": ("warm", {"dark_brown", "light_brown", "green"}, {"brown", "brown_black", "red"},{"fair","white","golden","brown"}),#B
    "Deep Autumn": ("warm", {"blue", "green", "gray", "black"}, {"black", "brown_black", "brown", "red"},{"brown","beige","golden","dark_brown"}),#B
    "Soft Autumn": ("warm", {"light_brown", "green"}, {"blonde", "brown", "red"},{"fair","white","golden","brown"}), #B
    "Cool Winter": ("cool", {"blue", "gray", "light_brown"}, {"blonde", "gray, brown_black", "black"},{"fair","white","golden","brown","beige","dark_brown"}), #B
    "Soft Summer": ("neutral", {"light_brown", "gray", "blue"}, {"brown_black", "brown", "gray"},{"brown","beige","dark_brown"}),#B
    "Cool Summer": ("cool", {"dark_brown", "gray", "black"}, {"black", "brown_black", "brown"},{"brown","beige","dark_brown"}), #B
    "Light Summer": ("neutral", {"blue", "gray", "green"}, {"blonde", "gray"},{"fair","white","golden"}),#B
    "Light Spring": ("warm", {"blue", "green", "light_brown"}, {"blonde", "brown"},{"fair","white","golden"}),#B
    "Deep Winter": ("cool", {"dark_brown", "gray", "black"}, {"black", "brown_black"},{"fair","white","golden","brown","beige","dark_brown"}) #B
}
    
    season_final = None
    # Iterate over the seasons and check if the individual matches any of the rules
    for season, (season_undertone, season_iris_colors, season_hair_colors, skin_colors) in seasons.items():
        if undertone in (season_undertone, "neutral") and iris_color in season_iris_colors and hair_color in season_hair_colors and skin_color in skin_colors:
            print("your season could be: ", season)
            season_final = season    
    # If no matching season is found, return None
    return season_final

def process_image(image_path):
    image = cv2.imread(image_path)
    
    # Check if the image loading was successful
    if image is None:
        print("Error: Unable to load the image.")
        return None
    
    undertone = detect_undertones(image)
    print("Undertone: ",undertone)
    iris_color = detect_iris_color(image)
    print("Iris Color: ",iris_color)
    hair_color = detect_hair_color(image)
    print("Hair Color: ",hair_color)
    skin_color = detect_skin_color(image)
    print("Skin Color: ", skin_color)
    # gender, age = detect_gender_and_age(image)
    season = define_season(undertone.lower().replace(" ", "_"),iris_color.lower().replace(" ", "_"),hair_color.lower().replace(" ", "_"), skin_color.lower().replace(" ", "_"))
    return undertone, iris_color, hair_color, skin_color, season

def get_suggested_colors(season_name):
    suggested_colors = {
        "Clear Spring": ["#FFFFFF", "#9E9FA1", "#1E1951 ", "#3697C2", "#53A396", "#4D884E", "#65AF58", "#F277AD", "#EFB0C3","#7063A8", "#E9692C", "#FFD43A"],
        "Warm Spring": ["#E1C6B3", "#AD8E79", "#80624A", "#56381E", "#98C6A9", "#53A396", "#4D884E", "#C2C2E2", "#E3506A","#E9692C", "#F1A02D", "#FFD43A"],
        "Clear Winter": ["#FFFFFF", "#9E9FA1", "#98C6A9", "#345A5D", "#C1C2E1","#96B3DF", "#3697C2", "#1E1951", "#EFB0C3", "#773752","#5D447B", "#7063A8"],
        "Warm Autumn": ["#E1C6B3", "#AD8E79", "#80624A", "#56381E", "#67682F", "#4D884E", "#809254", "#FFD43A", "#F1A02D","#E9692C", "#750C1A", "#A61F25"],
        "Deep Autumn": ["#AD8E79", "#56381E", "#67682F", "#305C39", "#4D884E", "#345A5D", "#750C1A", "#A61F25", "#D8242D","#E9692C", "#B65329", "#F1A02D"],
        "Soft Autumn": ["#E1C6B3", "#AD8E79", "#80624A", "#975F60", "#B65329", "#F1A02D", "#FFD43A", "#53A396", "#355E8A","#345A5D", "#4D884E", "#809254"],
        "Cool Winter": ["#FFFFFF", "#E1C6B3", "#AD8E79", "#9E9FA1", "#98C6A9", "#65AF58", "#3697C2", "#C1C2E1", "#F277AD","#EFB0C3", "#F3B256", "#FBE29F"],
        "Soft Summer": ["#FFFFFF", "#9E9FA1", "#6D6E72", "#442753", "#5D447B", "#750C1A", "#773752", "#975F60", "#355E8A","#C1C2E1", "#98C6A9", "#FBE29F"],
        "Cool Summer": ["#9E9FA1", "#96B3DF", "#3697C2", "#355E8A", "#1E1951", "#345A5D", "#98C6A9", "#C1C2E1", "#773752","#442753", "#750C1A", "#A61F25"],
        "Light Summer": ["#FFFFFF", "#E1C6B3", "#AD8E79", "#9E9FA1", "#975F60", "#773752", "#EFB0C3", "#C1C2E1", "#96B3DF","#3697C2", "#355E8A", "#98C6A9"],
        "Light Spring": ["#FFFFFF", "#E1C6B3", "#AD8E79", "#9E9FA1", "#98C6A9", "#65AF58", "#3697C2", "#C1C2E1", "#F277AD","#EFB0C3", "#F3B256", "#FBE29F"],
        "Deep Winter": ["#FFFFFF", "#000000", "#6D6E72", "#9E9FA1", "#1E1951", "#345A5D", "#355E8A", "#3697C2", "#F277AD","#5D447B", "#750C1A", "#D8242D"],
    }
    
    return suggested_colors.get(season_name, [])

def create_payload(base64_image,prompt):
    return {
        "model": "gpt-4-turbo-2024-04-09",
        "response_format":{"type":"json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300,
    }

async def preprocess_image(file):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, detail="File must be a JPEG or PNG image")

    # Save the image to a temporary file
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(contents)
        image_path = temp.name  # Get the path to the temporary file

    # Process the image
    resize_image(image_path)
    base64_image = encode_image(image_path)

    # Delete the temporary file
    os.remove(image_path)
    return base64_image