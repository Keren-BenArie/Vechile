import Reader
import Report

path = "report_1.eml"


def operate():
    readerEML = Reader.ReaderEML('EML', path)
    readerEML.read()
    jpegFiles = readerEML.attachments
    readerJPEG = Reader.ReaderJPEG('JPEG', path, jpegFiles)
    readerJPEG.read()


if __name__ == '__main__':
    operate()
