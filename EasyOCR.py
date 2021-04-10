import easyocr
reader = easyocr.Reader(['fr']) # need to run only once to load model into memory
result = reader.readtext('./Image/test7.jpg')
print(result)
