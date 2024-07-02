def mapear(valor, min_origem, max_origem, min_destino, max_destino):
    # Fórmula de interpolação linear
    return int(min_destino + (max_destino - min_destino) * (valor - min_origem) / (max_origem - min_origem))



def move_to(target,current,acc):
    delta_error =  target - current  
    new_pos = delta_error/(acc*1000) 
    return int(current + new_pos)

# current = 180
# import time
# while True:

#     current =  move_to(0,current,50)
#     print(int(current))
#     if(current == 180):
#         break

def saturate(num,max,mim):
#saturate the number betwen a interval 
    if(num>max):
        num = max 
    if(num<mim):
        num = mim 
    return num 