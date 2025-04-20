import hashlib
import manipulation_frame 
from manipulation_frame import convert_response_to_dictionary, create_frame_confirmation, create_frame_md5, create_data_frame_authentication

def make_autentication(gas_in_bytes, client):
    
    client.send(create_data_frame_authentication(gas_in_bytes, 0)) #enviando gas
    
    response = client.recv(4096 + 120) #pegando o ack        
    frame = convert_response_to_dictionary(response) #convertendo para um dicionário
            
    response = client.recv(4096 + 120)
    frame = convert_response_to_dictionary(response) #recebendo o data "atenticação completa"
        
    client.send(create_frame_confirmation(0)) #envia a confirmação de recebimento - flag ack
        
    md5_hash = hashlib.md5(frame['data'][:-1].encode('ascii')) #cria o md5 sem o \n
    
    frame_md5 = create_frame_md5(md5_hash, 1)
    client.send(frame_md5)
    
    response = client.recv(4096 + 120)
    frame = convert_response_to_dictionary(response)
    