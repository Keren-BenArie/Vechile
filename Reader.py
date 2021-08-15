from abc import ABC, abstractmethod
from email.header import decode_header
import email
from email import policy
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import GPSTAGS
import pytesseract
from PIL.ExifTags import TAGS
import qrtools
from pyzbar.pyzbar import decode
import pyzbar
import qrcode

class Reader(ABC):
    def __init__(self, readerType, path):
        self.readerType = readerType
        self.path = path


class ReaderEML(Reader):

    def __init__(self, readerType, path):
        super().__init__(readerType, path)
        self.emlFile = None
        self.attachments = []

    def read(self):
        with open(self.path, 'rb') as fp:  # select a specific email file from the list
            self.emlFile = fp
            mimeEmailContent = email.message_from_binary_file(self.emlFile, policy=policy.default)

        for part in mimeEmailContent.walk():
            if "attachment" in str(part.get("Content-Disposition")):
                filename = self.readableHeader(part.get_filename())
                partContents = part.get_payload(decode=True)
                self.attachments.append(filename)
                open('{}.jpg'.format(filename), 'wb').write(partContents)
                # what to do when already exists

    def readableHeader(self, h):
        rawHeader = decode_header(h)
        header = []
        for part, encoding in rawHeader:
            if type(part) == bytes:
                header.append(part.decode(encoding) if encoding is not None else part.decode('ascii'))
            else:
                header.append(part)
        return header


class ReaderJPEG(Reader):
    def __init__(self, readerType, path, jpegFiles):
        super().__init__(readerType, path)
        self.coords = None
        self.odometerRead = None
        self.jpegFiles = jpegFiles
        self.date = None

    def getGeotagging(self, exif):
        if not exif:
            raise ValueError("No EXIF metadata found")

        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif:
                    raise ValueError("No EXIF geotagging found")

                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]

        return geotagging

    def getDecimalFromDms(self, dms, ref):

        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0

        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds

        return round(degrees + minutes + seconds, 5)

    def getCoordinates(self, geotags):
        lat = self.getDecimalFromDms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])

        lon = self.getDecimalFromDms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

        return (lat, lon)

    def getLabeledExif(self, exif):
        labeled = {}
        for (key, val) in exif.items():
            labeled[TAGS.get(key)] = val
        return labeled

    def getTextFromImage(self, fileName):
        im = cv2.imread(fileName)
        Y, X = np.where(np.all(im == [0, 0, 255], axis=2))

        # A text file is created and flushed
        file = open("recognized.txt", "w+")
        file.write("")
        file.close()

        # Looping through the identified contours
        # Then rectangular part is cropped and passed on
        # to pytesseract for extracting text from it
        # Extracted text is then written into the text file
        # Cropping the text block for giving input to OCR

        # Get list of X,Y coordinates of red pixels
        # print(cropped)
        # cv2.imshow('cropped', cropped)
        # cv2.waitKey(0)

        # Open the file in append mode
        file = open("recognized.txt", "a")

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(im)

        # Appending the text into file
        file.write(text)
        file.write("\n")

        # Close the file
        file.close()

        # print(X, Y)


    def read(self):
        for jpeg in self.jpegFiles:
            fileName = str(jpeg) + ".jpg"
            image = Image.open(fileName)
            image.verify()

            # get date and coords from jpeg
            exif = image._getexif()
            geotags = self.getGeotagging(exif)
            labeled = self.getLabeledExif(exif)
            self.coords = self.getCoordinates(geotags)
            self.date = datetime.strptime(labeled['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')

            # get text from jpeg
            self.getTextFromImage(fileName)

            # read QR code from jpeg




class ReaderQR(Reader):
    def __init__(self, readerType, data, QR):
        super().__init__(readerType, data)
        self.QR = QR
        self.licensePlateNumber = None


class ReaderFactory:
    # checks which type of reader it is and create it
    pass
