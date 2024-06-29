def mapear(valor, min_origem, max_origem, min_destino, max_destino):
    # Fórmula de interpolação linear
    return min_destino + (max_destino - min_destino) * (valor - min_origem) / (max_origem - min_origem)