import cv2
import numpy as np




def overlay(image, data, color=(0,0,255), thickness=5,text=" "):
	x,y,radius=data
	#print("radius", radius)
	radius = int(radius*1000)
	#print("radius", radius)
	if radius<1:
		radius=1
	else:
		radius = int(radius)
	if(not text==" "):
		radius=15
	img=image.copy()
	img=cv2.circle(img, (x,y) , (radius), (255,0,0),thickness)
	img=cv2.circle(img, (x,y) , (radius+2), color,thickness)
	img=overlayText(img, x,y,text, radius)
	return img

def overlayText(img, x,y, text,radius=8):
	font=cv2.FONT_HERSHEY_SIMPLEX
	bgcolor=(255,255,255)
	fontcolor=(0,0,0)
	bgthickness=5
	fontthickness=bgthickness-3
	textSize, baseline = cv2.getTextSize(text, font, 1, bgthickness)
	textSizeWidth, textSizeHeight = textSize
	img=cv2.putText(img,text,(x-int(textSizeWidth/2), y+textSizeHeight+radius), font, 1, bgcolor, bgthickness)
	img=cv2.putText(img,text,(x-int(textSizeWidth/2), y+textSizeHeight+radius), font, 1, fontcolor, fontthickness)
	return img

def display(image,title="Image"):
	cv2.imshow(title,image)
	cv2.waitKey(0)


def cropImage(image,center, xmax,ymax , m=100):
	x,y,rad=center
	xmin=0
	ymin=0
	minx=max(xmin,int(x-(m-m%2)/2))
	miny=max(ymin, int(y-(m-m%2)/2))
	maxx=min(xmax,(minx+m))
	maxy=min(ymax,(miny+m))
	return image[miny:maxy,minx:maxx]


def addGaussianNoise(image, m=100):
	row,col,ch= image.shape
	mean = 0
	var = 0.1
	sigma = var**0.5
	gauss = np.random.normal(mean,sigma,(row,col,ch))

	gauss = gauss.reshape(row,col,ch).astype(np.uint8)
	noisy=cv2.add(image,gauss)
	return noisy
