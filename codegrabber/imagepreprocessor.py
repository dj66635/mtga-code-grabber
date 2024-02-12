import cv2
import PIL
import numpy
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

contour_th = 0.4  # what to consider a contour compared to the biggest one
gray_ths = 160, 190 # thresholds to perform multiple binary thresholdings to a graysacale image
gray_th_max = 225 # 'black' value after thesholding

optimal_height = 123 # empirically-found best size for the code boxes
optimal_width = 650 # about 5.3 width-to-heigth ratio

optimistic = False # based on tests we could skip croping by boundingRect

def preProcess(img, debug=0):
    img = numpy.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    # Threshold to find white regions
    grayImg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # test RGB
    thresholdImgs = [thresholdGray(grayImg, gray_th, gray_th_max) for gray_th in gray_ths]
    thresholdImgRef = thresholdImgs[0] # need to pick one to work on. Better results than on original or grayscale
    
    if debug >= 1: 
        for thImg in thresholdImgs: 
            printCv2Img(thImg)

    # Find box code contours
    bigContours = flatten([findBigContours(thresholdImg, contour_th) for thresholdImg in thresholdImgs])
    # bigContours = removeQuasiDuplicates(bigContours) # sometimes removes important contours, althougth speeds up the process
    
    if debug >= 1:
        print(f'Detected {len(bigContours)} contours')
        imgS = cv2.drawContours(img.copy(), bigContours, -1, (0,255,0), 3)
        printCv2Img(imgS)

    # Two ways to define bounding rectangles, the first one more 'fitted' and 'straightened'
    codeBoxes = [cropMinAreaRect(thresholdImgRef, contour) for contour in bigContours]
    if not optimistic: codeBoxes += [cropBoundingRect(thresholdImgRef, contour) for contour in bigContours]
   
    codeBoxes = [resize(box, optimal_width, optimal_height) for box in codeBoxes]
    codeBoxes += [erode(box) for box in codeBoxes]
    
    imgs = [PIL.Image.fromarray(box) for box in codeBoxes]
    return imgs

    
def findBigContours(img, th):
    contours = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    biggestContour = cv2.contourArea(max(contours, key=cv2.contourArea))
    bigContours = []
    for contour in contours:
        if cv2.contourArea(contour) > biggestContour * th:
            bigContours.append(contour)
    return bigContours

def cropBoundingRect(img, contour):
    x,y,w,h = cv2.boundingRect(contour)
    imgCrop = img[y:y+h, x:x+w]
    return imgCrop

def cropMinAreaRect(img, contour):
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = numpy.int0(box)
    width, height = int(rect[1][0]), int(rect[1][1])
    src_pts = box.astype('float32')
    dst_pts = numpy.array([[0, height-1], [0, 0], [width-1, 0], [width-1, height-1]], dtype='float32')
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    img_crop = cv2.warpPerspective(img, M, (width, height))
    return img_crop

def erode(img):
    kernel = numpy.ones((3, 3), numpy.uint8)  # no clue whats this parameter
    eroded = cv2.erode(img, kernel, iterations=1)
    return eroded

def thresholdGray(img, th, thMax):
    _, threshold = cv2.threshold(img, th, thMax, cv2.THRESH_BINARY)
    # threshold = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 1001, 2)
    # threshold = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 555 ,2)
    return threshold
    
def resize(box, targetW, targetH):
    w2h = targetW / targetH
    h, w = box.shape[:2]
    
    if min(h, w) == w: # if vertical, swap
        h, w = w, h

    scaleFactor = targetW / w
    if w > w2h * h: # too long, adjust by height
    	scaleFactor = targetH / h
    
    resizedBox = cv2.resize(box, None, fx = scaleFactor, fy = scaleFactor)
    return resizedBox

def printCv2Img(cvImg):
    imgS = PIL.Image.fromarray(cvImg)
    display(imgS.resize(int(0.2*s) for s in imgS.size))
    
def flatten(xss):
    return [x for xs in xss for x in xs]

# UNUSED
def deskew(image):
    coords = numpy.column_stack(numpy.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

# UNUSED
def fixContour(contour):
    peri = cv2.arcLength(contour, True)
    fixedContour = cv2.approxPolyDP(contour, 0.01 * peri, True)
    if len(fixedContour) == 4:
        return fixedContour
    else:
       return contour
    
# UNUSED
def dilate(img):
    kernel = numpy.ones((3, 3), numpy.uint8) 
    dilated = cv2.dilate(img, kernel, iterations=1)
    return dilated

# UNUSED
def removeNoise(img):
    return cv2.medianBlur(img, 5)

# UNUSED
def removeQuasiDuplicates(contourList):
    finalList = []
    for i in range(len(contourList)):
        isDup = False
        for j in range(i+1, len(contourList)):
            if similarContours(contourList[i], contourList[j]):
                isDup = True
                break
        if not isDup:
            finalList.append(contourList[i])
    return finalList

# UNUSED       
def similarContours(contour1, contour2):
    return cv2.matchShapes(contour1, contour2, cv2.CONTOURS_MATCH_I3, 0.0) < 0.02
        