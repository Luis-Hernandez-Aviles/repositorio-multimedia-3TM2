#Binary filter: Black and White

file = open('./images/example001.bmp','rb')
fileo = open('./images/example001bin.bmp','wb')
metadata = file.read(54)
fileo.write(metadata)
blanco = [0xff,0xff,0xff]
negro = [0x00,0x00,0x00]

file.seek(54,0)
no_pix = 0
limite = (pow(2, 24)-1)/2
while(True):
    pixel_data = file.read(3)
    if(len(pixel_data) > 0):
        valor_int = int.from_bytes(bytes(pixel_data),byteorder='little')
        if(valor_int<limite):
            fileo.write(bytes(blanco))
        else:
            fileo.write(bytes(negro))
        no_pix += 1
    else:
        break
print('No Pixels: '+str(no_pix))
file.close()
fileo.close()
