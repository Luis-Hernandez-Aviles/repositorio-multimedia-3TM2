#Read and display data from BMP

file = open("./images/example001.bmp","rb")

firm = file.read(2)
print(firm)
file.seek(54,0)
pixel_first = file.read(3)
print(pixel_first)

file.seek(54,0)
no_pix = 0
while(True):
    pixel_data = file.read(3)
    if(len(pixel_data) > 0):
        print(pixel_data)
        no_pix += 1
    else:
        break
print('No Pixels: '+str(no_pix))
file.close()
