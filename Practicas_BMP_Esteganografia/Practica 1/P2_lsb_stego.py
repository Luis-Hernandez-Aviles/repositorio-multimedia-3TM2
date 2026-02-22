import struct
import math
import os

def leer_bmp(filepath):
    """Retorna (header_bytes, pixels, width, height, row_size)"""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    offset = struct.unpack_from('<I', data, 10)[0]
    width = struct.unpack_from('<i', data, 18)[0]
    height = struct.unpack_from('<i', data, 22)[0]
    
    row_size = (width * 3 + 3) & ~3
    header = bytearray(data[:offset])
    pixels = bytearray(data[offset:])
    return header, pixels, width, height, row_size

def guardar_bmp(filepath, header, pixels):
    """Guarda los bytes en un nuevo archivo BMP"""
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixels)

def embed_lsb(src_path, dst_path, mensaje):
    """Oculta un mensaje usando la técnica LSB"""
    header, pixels, width, height, row_size = leer_bmp(src_path)
    msg_bytes = mensaje.encode('utf-8')
    msg_len = len(msg_bytes)
    
    # Encabezado de 32 bits con la longitud + mensaje
    datos = struct.pack('<I', msg_len) + msg_bytes
    
    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    
    if len(bits) > len(pixels):
        raise ValueError('Mensaje demasiado largo para esta imagen') [cite: 78, 127]

    pixels_mod = bytearray(pixels)
    for idx, bit in enumerate(bits):
        pixels_mod[idx] = (pixels_mod[idx] & 0xFE) | bit
        
    guardar_bmp(dst_path, header, pixels_mod)
    print(f"[OK] Mensaje de {msg_len} bytes incrustado en {dst_path}")

def extract_lsb(stego_path):
    """Recupera el mensaje oculto en la imagen"""
    header, pixels, width, height, row_size = leer_bmp(stego_path)
    
    # 1. Leer los primeros 32 bits (longitud)
    len_bits = [pixels[i] & 1 for i in range(32)]
    
    # 2. Reconstruir esos bits en 4 bytes
    len_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in len_bits[i:i+8]:
            byte = (byte << 1) | bit
        len_bytes.append(byte)
        
    # 3. Desempaquetar respetando el formato Little Endian ('<I') 
    msg_len = struct.unpack('<I', len_bytes)[0]
    
    # 4. Calcular los bits totales a leer
    total_bits = 32 + (msg_len * 8)
    
    # Control de seguridad extra para evitar el IndexError
    if total_bits > len(pixels):
        return f"Error: La longitud extraída ({msg_len} bytes) excede la imagen."
        
    # 5. Extraer los bits del mensaje y reconstruirlos
    msg_bits = [pixels[i] & 1 for i in range(32, total_bits)]
    
    msg_bytes = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        msg_bytes.append(byte)
        
    return msg_bytes.decode('utf-8')

def calcular_psnr(original_path, stego_path):
    """Calcula MSE y PSNR para evaluar la degradación visual"""
    header_o, pix_orig, w, h, rs = leer_bmp(original_path)
    header_s, pix_steg, _, _, _ = leer_bmp(stego_path)
    
    # Error Cuadrático Medio (MSE) 
    mse = sum((a - b)**2 for a, b in zip(pix_orig, pix_steg)) / (w * h * 3)
    
    if mse == 0:
        return 0.0, float('inf')
        
    # Relación señal-ruido de pico (PSNR)
    psnr = 10 * math.log10(255**2 / mse)
    return mse, psnr  # Retorna ambos explícitamente

# --- PRUEBAS DE LABORATORIO ---
if __name__ == "__main__":
    IMG_200 = 'Img200.bmp' 
    IMG_512 = 'Img512.bmp'

    # --- PRUEBA 1: 200x200 ---
    if os.path.exists(IMG_200):
        print("\n--- Ejecutando Prueba 1 (200x200) ---")
        STEGO_200 = 'stego_200.bmp'
        embed_lsb(IMG_200, STEGO_200, "PRUEBA 200 PX")
        msg_1 = extract_lsb(STEGO_200)
        mse_1, psnr_1 = calcular_psnr(IMG_200, STEGO_200)
        # Código que ayuda en eliminar el texto que causaba el NameError
        print(f"Mensaje: {msg_1}")
        print(f"MSE: {mse_1:.6f} | PSNR: {psnr_1:.2f} dB")
    
    # --- PRUEBA 2: 512x512 ---
    if os.path.exists(IMG_512):
        print("\n--- Ejecutando Prueba 2 (512x512) ---")
        STEGO_512 = 'stego_512.bmp'
        embed_lsb(IMG_512, STEGO_512, "MENSAJE PARA LA IMAGEN GRANDE UPIITA")
        msg_2 = extract_lsb(STEGO_512)
        mse_2, psnr_2 = calcular_psnr(IMG_512, STEGO_512)
        print(f"Mensaje: {msg_2}")
        print(f"MSE: {mse_2:.6f} | PSNR: {psnr_2:.2f} dB")
    else:
        print(f"\nNo se encontró {IMG_512}")
    
    # --- PRUEBA 3: Capacidad Máxima (512x512) ---
    if os.path.exists(IMG_512):
        print("\n--- Ejecutando Prueba 3 (Capacidad Máxima 512x512) ---")
        STEGO_MAX = 'stego_max.bmp'
        
        # Creamos un mensaje de 98,300 caracteres
        mensaje_max = "A" * 98300 
        
        try:
            embed_lsb(IMG_512, STEGO_MAX, mensaje_max)
            msg_rec = extract_lsb(STEGO_MAX)
            mse_max, psnr_max = calcular_psnr(IMG_512, STEGO_MAX)
            
            print(f"Mensaje recuperado con éxito (Longitud: {len(msg_rec)})")
            print(f"MSE: {mse_max:.6f} | PSNR: {psnr_max:.2f} dB")
            print("--- PRUEBAS FINALIZADAS ---")
        except ValueError as e:
            print(f"Error esperado: {e}")