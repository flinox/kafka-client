## Programa para consumir mensagens no kafka
##
## usage: consumer.py [-h] topico consumerid acks mockar qtde
## 
## positional arguments:
##   topico                Informe o nome do topico que deseja consumir as mensagens!
## 
## optional arguments:
##   -h, --help              show this help message and exit
##
##   topico TOPICO         Informe o nome do topico que deseja ler as mensagens
##   messagetype AVRO/JSON Informe se o layout das mensagens do topico é AVRO ou JSON!
##   --keyserialized       Informe se a também deve ser deserializada AVRO, default False!
##   --groupid GROUPID     Informe o nome do group_id, padrão é kapacitor
##   --offset OFFSET       Informe se a leitura do offset será earliest ou latest
## 
## python consumer.py account-created AVRO --keyserialized True --groupid kapacitor --offset latest

from datetime import datetime
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import time
import json
import argparse
import re
import os


def getProperties(key=''):
    
    propertiesFile = os.environ['PROPERTIES']
    """
    Reads a .properties file and returns the key value pairs as dictionary.
    if key value is specified, then it will return its value alone.
    """
    with open(propertiesFile) as f:
        l = [line.strip().split("=") for line in f.readlines() if not line.startswith('#') and line.strip()]
        d = {key.strip(): value.strip() for key, value in l}

        if key:
            return d[key]
        else:
            return d


def get_schema_registry(url,api_key,secret_key,topico,keyserialized):

    key_avro_deserializer = None
    value_avro_deserializer = None
    key_fields_schema = None
    value_fields_schema = None
    Error = False
    schema_registry_conf = {'url'                 : url,
                            'basic.auth.user.info': '{}:{}'.format(api_key,secret_key)}
        
    try:

        with SchemaRegistryClient(schema_registry_conf) as schema_registry_client:
    
            # Schema Registry Pegando a última versão dos schemas (key/value)
            value_schema = schema_registry_client.get_latest_version('{}-value'.format(topico))
            value_avro_deserializer = AvroDeserializer(schema_registry_client,value_schema.schema.schema_str)

            # Schema string to json
            value_json_schema = json.loads(value_schema.schema.schema_str)
            value_fields_schema = value_json_schema['fields']


            if keyserialized:

                # Schema Registry Pegando a última versão dos schemas (key/value)
                key_schema = schema_registry_client.get_latest_version('{}-key'.format(topico))
                key_avro_deserializer = AvroDeserializer(schema_registry_client,key_schema.schema.schema_str)

                # Schema string to json
                key_json_schema = json.loads(key_schema.schema.schema_str)
                key_fields_schema = key_json_schema['fields']

    except Exception as e :
        print('>>> ERROR get_schema_registry()')
        print('>>> {}'.format(e))
        Error = True
    
   
    return key_avro_deserializer, value_avro_deserializer, key_fields_schema, value_fields_schema, Error




def get_parameters():
    try:

        params = {}

        # Define os parametros esperados e obrigatorios
        parser = argparse.ArgumentParser()
        parser.add_argument("topico", help="Informe o nome do topico que deseja ler as mensagens!")
        parser.add_argument("messagetype", help="Informe se o layout das mensagens do topico é AVRO ou JSON!")        
        parser.add_argument("--keyserialized", help="Informe se a também deve ser deserializada AVRO", default=False )
        parser.add_argument("--groupid", help="Informe o nome do group_id, padrão é kapacitor", default="kapacitor" )
        parser.add_argument("--offset", help="Informe o offset commit desejado, padrão é latest", default="latest" )
        args = parser.parse_args()

        # Pega os argumentos passados
        params['topico'] = args.topico
        params['groupid'] = args.groupid    
        params['offset'] = args.offset   
        params['keyserialized'] = args.keyserialized 
        params['messagetype'] = args.messagetype    

        print('#'*80)
        print('   Kafka Cluster        : {}'.format(getProperties('kafka-broker')))
        print('   Schema Registry Url  : {}'.format(getProperties('schemaregistry-url')))
        print('')
        print('   Topico               : {}'.format(params['topico']))
        print('   Consumer Group ID    : {}'.format(params['groupid']))
        print('   Offset               : {}'.format(params['offset']))    
        print('#'*80)
    
    except Exception as e :
        print('>>> ERROR 0002\n     {}\n     {}\n     {} - {}'.format(e.__class__,e.__doc__,e.strerror,e))  

    return params



def set_consumer(params,broker):

    try:

        url = re.compile(r"https?://(www\.)?")
        kafka_broker = url.sub('', broker).strip().strip('/')
        string_deserializer = StringDeserializer('utf_8')


        kafka_conf = {'bootstrap.servers': kafka_broker,
                    'group.id': params['groupid'],
                    'auto.offset.reset': params['offset'],
                    'ssl.endpoint.identification.algorithm':'https',
                    'security.protocol':'SASL_SSL',
                    'sasl.mechanisms':'PLAIN',
                    'sasl.username':getProperties('kafka-username'),
                    'sasl.password':getProperties('kafka-password'),
                    'key.deserializer': (key_avro_deserializer if (params['keyserialized'] and params['messagetype'] == 'AVRO') else string_deserializer),
                    'value.deserializer': value_avro_deserializer if (params['messagetype'] == 'AVRO') else string_deserializer} 
                        
    except Exception as e :
        print('>>> ERROR set_consumer()')
        print('>>> {}'.format(e))
        exit(1)    

    return DeserializingConsumer(kafka_conf)





def show_messages(params):
    consumer = set_consumer(params,getProperties('kafka-broker'))

    try:
        consumer.subscribe([params['topico']])

        timeout = time.time() + 20

        data = ""
        while True:
            msg = consumer.poll(timeout)

            if msg is None:
                time.sleep(5)
                continue
            if msg.error():
                print(">>> ERROR main() Consumer error: {}".format(msg.error()))
                continue

            print('-'*80)
            print('    Received Message!')
            print(' ')
            print('    Topic    :',msg.topic())
            print('    Partition:',msg.partition())
            print('    Offset   :',msg.offset())
            print(' ')
            print('    Message')
            print('    ----------------')

            if params['messagetype'] == 'AVRO':

                if type(msg.value()) is dict:
                    for k, v in msg.value().items():
                        print('    Key  :',k)
                        print('    Value:',v)
                        print('    ===============================================================')            
                else:
                    print(msg.value())
                    
            else:
                print('    Key      :',msg.key())
                print('    Message  :',msg.value())

    except Exception as e :
        print('>>> ERROR main() consuming messages!')
        print('>>> {}'.format(e))
        time.sleep(60)

    except KeyboardInterrupt:
        print('\n>>> Programa encerrado manualmente!')
        exit(0)

    finally:
        print('>>> Closing consumer!')
        consumer.unsubscribe()
        consumer.close()



# Espera para tentar novamente
# async def waiting(retry,tries):
#     await asyncio.sleep(retry)
#     tries -= 1
#     return tries

# Espera para tentar novamente
def waiting(retry,tries):
    time.sleep(retry)
    tries -= 1
    return tries





# BEGIN
########################################################################################################

# Pega os parametros informados
print('#'*80)
print('   Iniciado o programa as ',datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

retry = 10
tries = 5
Error = False

# Pega os parametros informados
params = get_parameters()

while True:

    # Pega o schema serializado da key/value e os campos do ultimo schema do schema registry
    if params['messagetype'] == 'AVRO':
        key_avro_deserializer, value_avro_deserializer, key_fields_schema, value_fields_schema, Error = get_schema_registry(getProperties('schemaregistry-url'),getProperties('schemaregistry-username'),getProperties('schemaregistry-password'),params['topico'],params['keyserialized'])


    if Error:
        print('\n    Aguardando {} segundos para tentar buscar schema novamente, {} tentativas restantes...\n'.format(retry,tries))
        
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # tries = loop.run_until_complete(waiting(retry,tries))
        tries = waiting(retry,tries)

        if tries == 0:
            break

        continue
    else:
        break

if not Error:
    show_messages(params)
else:
    print('    Encerrando o programa as ',datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print('#'*80)
    exit(1)     


print('Done!')
print('#'*80)

