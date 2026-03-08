import hashlib
import struct
import random
import os
import math

# --- 1. FUNCIONES BASE (PRÁCTICA 1) --- [cite: 321-348, 401-411]
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
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixels)

def calcular_psnr(original_path, stego_path):
    _, pix_orig, w, h, _ = leer_bmp(original_path)
    _, pix_steg, _, _, _ = leer_bmp(stego_path)
    mse = sum((float(a) - float(b))**2 for a, b in zip(pix_orig, pix_steg)) / (w * h * 3)
    if mse == 0: return float('inf')
    psnr = 10 * math.log10(255**2 / mse)
    return mse, psnr

# --- 2. SEGURIDAD Y CIFRADO (PRÁCTICA 2) --- [cite: 436-459]
def derivar_clave(password: str, longitud: int) -> bytes:
    """Genera una clave usando SHA-256 en modo contador"""
    clave = b''
    contador = 0
    while len(clave) < longitud:
        bloque = hashlib.sha256(password.encode() + struct.pack('<I', contador)).digest()
        clave += bloque
        contador += 1
    return clave[:longitud]

def cifrar_xor(mensaje: bytes, password: str) -> bytes:
    clave = derivar_clave(password, len(mensaje))
    return bytes(m ^ k for m, k in zip(mensaje, clave))

def descifrar_xor(cifrado: bytes, password: str) -> bytes:
    return cifrar_xor(cifrado, password)

def semilla_de_password(password: str) -> int:
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes[:8], 'big')

def seleccionar_posiciones(total_bytes, n_bits, seed):
    """Selecciona índices únicos. FIX: Se usa una secuencia fija para consistencia"""
    rng = random.Random(seed)
    # Generamos todas las posiciones posibles y tomamos las necesarias
    # Esto asegura que los primeros 32 índices siempre sean los mismos
    pool = list(range(total_bytes))
    rng.shuffle(pool)
    return pool[:n_bits]

# --- 3. INCRUSTACIÓN Y EXTRACCIÓN SEGURA --- [cite: 460-516]
def embed_secure(src_path, dst_path, mensaje, password):
    header, pixels, _, _, _ = leer_bmp(src_path)
    msg_bytes = mensaje.encode('utf-8')
    msg_cifrado = cifrar_xor(msg_bytes, password)
    
    # Datos: 4 bytes longitud + mensaje cifrado
    datos = struct.pack('>I', len(msg_bytes)) + msg_cifrado
    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
            
    if len(bits) > len(pixels):
        raise ValueError('Mensaje demasiado grande')
        
    seed = semilla_de_password(password)
    posiciones = seleccionar_posiciones(len(pixels), len(bits), seed)
    
    pixels_mod = bytearray(pixels)
    for pos, bit in zip(posiciones, bits):
        pixels_mod[pos] = (pixels_mod[pos] & 0xFE) | bit
        
    guardar_bmp(dst_path, header, pixels_mod)
    print(f'[OK] Mensaje cifrado e incrustado en {dst_path}')

def extract_secure(stego_path, password):
    _, pixels, _, _, _ = leer_bmp(stego_path)
    seed = semilla_de_password(password)
    
    # 1. Obtener posiciones para la longitud (32 bits)
    # Usamos un pool grande para asegurar que coincidan con el embedding
    pool_indices = seleccionar_posiciones(len(pixels), len(pixels), seed)
    
    pos_longitud = pool_indices[:32]
    len_bits = [pixels[p] & 1 for p in pos_longitud]
    msg_len = 0
    for b in len_bits:
        msg_len = (msg_len << 1) | b
        
    # 2. Obtener posiciones para el mensaje
    total_bits = 32 + (msg_len * 8)
    pos_mensaje = pool_indices[32:total_bits]
    msg_bits = [pixels[p] & 1 for p in pos_mensaje]
    
    cifrado = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        cifrado.append(byte)
        
    return descifrar_xor(bytes(cifrado), password).decode('utf-8')

# --- 4. RETO OPCIONAL: IMAGEN EN IMAGEN --- [cite: 567-570]
def embed_image_in_image(cover_path, secret_path, output_path, password):
    with open(secret_path, 'rb') as f:
        secret_bytes = f.read()
    
    secret_cifrado = cifrar_xor(secret_bytes, password)
    datos = struct.pack('>I', len(secret_bytes)) + secret_cifrado
    
    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
            
    header, pixels, _, _, _ = leer_bmp(cover_path)
    if len(bits) > len(pixels):
        raise ValueError('La imagen secreta es muy grande para la portadora.')

    seed = semilla_de_password(password)
    posiciones = seleccionar_posiciones(len(pixels), len(bits), seed)
    
    pixels_mod = bytearray(pixels)
    for pos, bit in zip(posiciones, bits):
        pixels_mod[pos] = (pixels_mod[pos] & 0xFE) | bit
        
    guardar_bmp(output_path, header, pixels_mod)
    print(f'[RETO] Imagen {secret_path} oculta en {output_path}')

def extract_image_from_image(stego_path, output_secret_path, password):
    _, pixels, _, _, _ = leer_bmp(stego_path)
    seed = semilla_de_password(password)
    pool_indices = seleccionar_posiciones(len(pixels), len(pixels), seed)
    
    len_bits = [pixels[p] & 1 for p in pool_indices[:32]]
    file_len = 0
    for b in len_bits:
        file_len = (file_len << 1) | b
        
    total_bits = 32 + (file_len * 8)
    msg_bits = [pixels[p] & 1 for p in pool_indices[32:total_bits]]
    
    cifrado = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        cifrado.append(byte)
        
    secret_bytes = descifrar_xor(bytes(cifrado), password)
    with open(output_secret_path, 'wb') as f:
        f.write(secret_bytes)
    print(f'[RETO] Imagen recuperada como {output_secret_path}')

# --- 5. ANÁLISIS ESTADÍSTICO --- [cite: 539-556]
def chi_cuadrado_lsb(filepath):
    _, pixels, _, _, _ = leer_bmp(filepath)
    ceros = sum(1 for b in pixels if (b & 1) == 0)
    unos = len(pixels) - ceros
    esperado = len(pixels) / 2
    chi2 = ((ceros - esperado)**2 + (unos - esperado)**2) / esperado
    print(f'Archivo: {filepath} | χ² = {chi2:.4f} (LSBs 0:{ceros}, 1:{unos})')
    return chi2

# --- BLOQUE PRINCIPAL DE EJECUCIÓN ---
if __name__ == "__main__":
    # Nombres de archivos
    IMG_ORIGINAL = 'Img400.bmp'
    IMG_STEGO = 'stego_seguro.bmp'
    IMG_SECRETA = 'Img200.bmp' # Para el reto
    IMG_RETO_OUT = 'stego_reto.bmp'
    
    CLAVE = 'Telemática@2025'
    MSG = 'Datos confidenciales de la red 10.0.1.0/24'

    if os.path.exists(IMG_ORIGINAL):
        print("=== INICIANDO PRÁCTICA 2 ===")
        # 1. Proceso de Mensaje de Texto
        embed_secure(IMG_ORIGINAL, IMG_STEGO, MSG, CLAVE)
        recuperado = extract_secure(IMG_STEGO, CLAVE)
        print(f'Texto recuperado: "{recuperado}"')
        
        # 2. Análisis de Calidad y Estadística
        mse, psnr = calcular_psnr(IMG_ORIGINAL, IMG_STEGO)
        print(f'PSNR: {psnr:.2f} dB')
        
        print("\n=== ANÁLISIS CHI-CUADRADO ===")
        chi_cuadrado_lsb(IMG_ORIGINAL)
        chi_cuadrado_lsb(IMG_STEGO)
        
        # 3. Reto Opcional (Imagen dentro de Imagen)
        if os.path.exists(IMG_SECRETA):
            print("\n=== EJECUTANDO RETO OPCIONAL ===")
            embed_image_in_image(IMG_ORIGINAL, IMG_SECRETA, IMG_RETO_OUT, CLAVE)
            extract_image_from_image(IMG_RETO_OUT, 'recuperada_reto.bmp', CLAVE)
            _, psnr_reto = calcular_psnr(IMG_ORIGINAL, IMG_RETO_OUT)
            print(f'PSNR del Reto: {psnr_reto:.2f} dB')
    else:
        print(f"Error: Asegúrate de que {IMG_ORIGINAL} esté en la carpeta.")