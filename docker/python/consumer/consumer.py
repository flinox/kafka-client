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


from confluent_kafka.serialization import StringDeserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
import time
import json
import argparse
import re


def getProperties(key=''):
    propertiesFile ="../../_keys/environment.properties"
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


def get_schema_registry(url,api_key,secret_key,topico):

    key_avro_deserializer = None
    value_avro_deserializer = None
    key_fields_schema = None
    value_fields_schema = None

    try:
        schema_registry_conf = {'url'                 : url,
                                'basic.auth.user.info': '{}:{}'.format(api_key,secret_key)}
        
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

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
    
    return key_avro_deserializer, value_avro_deserializer, key_fields_schema, value_fields_schema




def get_parameters():
    try:

        # Define os parametros esperados e obrigatorios
        parser = argparse.ArgumentParser()
        parser.add_argument("topico", help="Informe o nome do topico que deseja ler as mensagens!")
        parser.add_argument("messagetype", help="Informe se o layout das mensagens do topico é AVRO ou JSON!")        
        parser.add_argument("--keyserialized", help="Informe se a também deve ser deserializada AVRO", default=False )
        parser.add_argument("--groupid", help="Informe o nome do group_id, padrão é kapacitor", default="kapacitor" )
        parser.add_argument("--offset", help="Informe o offset commit desejado, padrão é latest", default="latest" )
        args = parser.parse_args()

        # Pega os argumentos passados
        topico = args.topico
        keyserialized = args.keyserialized
        groupid = args.groupid    
        messagetype = args.messagetype
        offset = args.offset

        print('#'*80)
        print('   Topico        : {}'.format(topico))
        print('   Message Type  : {}'.format(messagetype))
        print('   Key Serialized: {}'.format(keyserialized))
        print('   Group_ID      : {}'.format(groupid))
        print('   Offset        : {}'.format(offset))    
        print('#'*80)
    
    except Exception as e :
        print('>>> ERROR get_parameters()')
        print('>>> {}'.format(e))
        exit(1)    

    return topico, messagetype, groupid, offset, keyserialized




def set_consumer(messagetype,broker):

    try:

        url = re.compile(r"https?://(www\.)?")
        kafka_broker = url.sub('', broker).strip().strip('/')
        string_deserializer = StringDeserializer('utf_8')

        if messagetype == 'AVRO':
            kafka_conf = {'bootstrap.servers': kafka_broker,
                        'group.id': groupid,
                        'auto.offset.reset': offset,
                        'ssl.endpoint.identification.algorithm':'https',
                        'security.protocol':'SASL_SSL',
                        'sasl.mechanisms':'PLAIN',
                        'sasl.username':getProperties('kafka-username'),
                        'sasl.password':getProperties('kafka-password'),
                        'key.deserializer': (key_avro_deserializer if keyserialized else string_deserializer),
                        'value.deserializer': value_avro_deserializer}
        else:
            kafka_conf = {'bootstrap.servers': kafka_broker,
                        'group.id': groupid,
                        'auto.offset.reset': offset,
                        'ssl.endpoint.identification.algorithm':'https',
                        'security.protocol':'SASL_SSL',
                        'sasl.mechanisms':'PLAIN',
                        'sasl.username':getProperties('kafka-username'),
                        'sasl.password':getProperties('kafka-password'),
                        'key.deserializer': string_deserializer,
                        'value.deserializer': string_deserializer}

                        
    except Exception as e :
        print('>>> ERROR set_consumer()')
        print('>>> {}'.format(e))
        exit(1)    

    return DeserializingConsumer(kafka_conf)





def show_messages():
    consumer = set_consumer(messagetype,getProperties('kafka-broker'))

    try:
        consumer.subscribe([topico])

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

            if messagetype == 'AVRO':

                if type(msg.value()) is dict:
                    for k, v in msg.value().items():
                        print('    Key  :',k)
                        print('    Value:',v)
                        print('    ===============================================================')            
                else:
                    print(msg.value())
                    
            else:
                print(type(msg.value()))
                print('    Message  :',msg.value())

    except Exception as e :
        print('>>> ERROR main() consuming messages!')
        print('>>> {}'.format(e))

    except KeyboardInterrupt:
        print('\n>>> Programa encerrado manualmente!')
        exit(0)

    finally:
        print('>>> Closing consumer!')
        consumer.unsubscribe()
        consumer.close()


# BEGIN
# Pega os parametros informados
topico, messagetype, groupid, offset, keyserialized = get_parameters()

# Pega o schema serializado da key/value e os campos do ultimo schema do schema registry
if messagetype == 'AVRO':
    key_avro_deserializer, value_avro_deserializer, key_fields_schema, value_fields_schema = get_schema_registry(getProperties('schemaregistry-url'),getProperties('schemaregistry-username'),getProperties('schemaregistry-password'),topico)




# Rotina para publicar as mensagens
show_messages()




print('Done!')
print('#'*80)

