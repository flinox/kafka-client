
## Programa para produzir mensagens no kafka
## python producer.py

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
import re
from datetime import datetime
  
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


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
        print('-'*80)
    else:
        print('')
        print('Message delivered!')
        print('   Topic    : {} '.format(msg.topic()))
        print('   Partition: {} '.format(msg.partition()))
        print('   Offset   : {} '.format(msg.offset()))
        print('-'*80)

def get_schema_of_topic(sr_url,sr_key,sr_secret,topico):

    try:

        # Schema Registry Configuration
        schema_registry_conf = {'url'                 : sr_url,
                                'basic.auth.user.info': '{}:{}'.format(sr_key,sr_secret)}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        # Schema Registry Pegando a última versão dos schemas (key/value)
        key_schema = schema_registry_client.get_latest_version('{}-key'.format(topico))
        value_schema = schema_registry_client.get_latest_version('{}-value'.format(topico))

        # Schema Registry Serializa a última versão dos schemas para avro (key/value) 
        key_avro_serializer = AvroSerializer(schema_registry_client,key_schema.schema.schema_str)
        value_avro_serializer = AvroSerializer(schema_registry_client,value_schema.schema.schema_str)

        # Schema string to json
        key_json_schema = json.loads(key_schema.schema.schema_str)
        key_fields_schema = key_json_schema['fields']

        value_json_schema = json.loads(value_schema.schema.schema_str)
        value_fields_schema = value_json_schema['fields']
    
    except Exception as e :
        print('>>> ERROR getting schema of topic!')
        print('>>> {}'.format(e))
        exit(1)
    
    return key_avro_serializer, value_avro_serializer, key_fields_schema, value_fields_schema

def get_parameters(params):
    
    # Pega os argumentos passados
    params['SR_URL'] = getProperties('schemaregistry-url')
    params['SR_API_KEY'] = getProperties('schemaregistry-username')
    params['SR_API_SECRET'] = getProperties('schemaregistry-password')
    params['KC_URL'] = getProperties('kafka-broker')    
    params['KC_API_KEY'] = getProperties('kafka-username')
    params['KC_API_SECRET'] = getProperties('kafka-password')
    params['PRODUCERID'] = 'ManualProducer'

    print('#'*80)
    print('   Kafka Cluster        : {}'.format(params['KC_URL']))
    print('   Schema Registry Url  : {}'.format(params['SR_URL']))
    print('   Producer ID          : {}'.format(params['PRODUCERID']))
    print('#'*80)

    return params

def set_producer(broker,producerid,kc_key,kc_secret,avro_key,avro_value):

    # kafka configuration

    url = re.compile(r"https?://(www\.)?")
    kafka_broker = url.sub('', broker).strip().strip('/')

    kafka_conf = {'bootstrap.servers': kafka_broker,
                'client.id': producerid,
                'security.protocol':'SASL_SSL',
                'sasl.mechanisms':'PLAIN',
                'sasl.username':kc_key,
                'sasl.password':kc_secret,
                'on_delivery': delivery_report,
                'acks':"1",
                'key.serializer': avro_key,
                'value.serializer': avro_value}

    return SerializingProducer(kafka_conf)

def set_mock_data_key(key_fields_schema):

    fake_key_data = {}
    fake_key = None

    print('-'*80)
    print('Message Key:')

    for field in key_fields_schema:

        # metadados do campo
        field_data = field

        if field_data['type'] == 'string':
            if field_data['name'] == 'id':
                fake_key_data[field_data['name']] = input("\n'{}' tipo string para a mensagem\n{} : ".format(field_data['name'],field_data['doc']))
                fake_key = fake_key_data[field_data['name']]                

    return fake_key, fake_key_data

def set_mock_data_value(fake_key,value_fields_schema):

    fake_value_data = {}
    print('')
    print('Message Value:')

    for field in value_fields_schema:

        # metadados do campo
        field_data = field

        if isinstance(field_data['type'], (list)):
            for fieldtypes in field_data['type']:

                # Se for campo de TIMESTAMP é um dict pra percorrer
                if isinstance(fieldtypes, (dict)):
                    if 'long' in fieldtypes['type']:
                        fake_value_data[field_data['name']] =  datetime.now()
                elif 'string' in fieldtypes:
                    fake_value_data[field_data['name']] = input("\n'{}' tipo string\n{} : ".format(field_data['name'],field_data['doc']))
                elif 'boolean' in fieldtypes:
                    fake_value_data[field_data['name']] = bool(input("\n'{}' tipo boolean (True/False)\n{} : ".format(field_data['name'],field_data['doc'])))
                elif 'int' in fieldtypes:
                    fake_value_data[field_data['name']] = int(input("\n'{}' tipo int\n{} : ".format(field_data['name'],field_data['doc'])))
                elif 'float' in fieldtypes:
                    fake_value_data[field_data['name']] = float(input("\n'{}' tipo float (separador .)\n{} : ".format(field_data['name'],field_data['doc'])))
                # else:
                #     fake_value_data[field_data['name']] = input("\n'{}' tipo um dos '{}' : ".format(field_data['name'],fieldtypes))

        elif field_data['type'] == 'string':

            if field_data['name'] == 'id':
                #print("Usando id '{}' gerado no momento da Message key".format(fake_key))
                fake_value_data[field_data['name']] = fake_key

            elif field_data['name'] in ('createuser','userCreated','userUpdated','updateuser'):
                fake_value_data[field_data['name']] = 'MOCKER'

            elif field_data['name'] == 'recordactive':
                fake_value_data[field_data['name']] = bool(input("\n'{}' tipo boolean (True/False)\n{} : ".format(field_data['name'],field_data['doc'])))
            
            elif field_data['name'] == 'status':
                fake_value_data[field_data['name']] = input("\n'{}' tipo string\n{} : ".format(field_data['name'],field_data['doc']))

            else:
                fake_value_data[field_data['name']] = input("\n'{}' tipo string\n{} : ".format(field_data['name'],field_data['doc']))

    return fake_value_data

# INICIO

params = {}
params = get_parameters(params)

produce = True
while produce:

    params['TOPICO'] = input("Informe o nome do topico que deseja produzir uma mensagem: ")

    key_avro_serializer, value_avro_serializer, key_fields_schema, value_fields_schema = get_schema_of_topic(params['SR_URL'],params['SR_API_KEY'],params['SR_API_SECRET'],params['TOPICO'])

    # Guarda o par da key/value gerado
    pair_key_value = {}

    # Schema Key Message
    ##########################
    fake_key, fake_key_data = set_mock_data_key(key_fields_schema)
    pair_key_value['key'] = fake_key_data

    #############
    # VALUE: para cada campo na lista de campos do schema de value
    fake_value_data = set_mock_data_value(fake_key,value_fields_schema)
    pair_key_value['value'] = fake_value_data

    # Adicionando o par key/value a lista
    list_key_value = []
    list_key_value.append(pair_key_value)

    print('-'*80)
    print('Producing Message on Topic {}'.format(params['TOPICO']))
    for key_value in list_key_value:

        key = key_value['key']
        value = key_value['value']

        try:
            print('Producing messages key: {}'.format(key_value['key']))
            producer = set_producer(params['KC_URL'],params['PRODUCERID'],params['KC_API_KEY'],params['KC_API_SECRET'],key_avro_serializer,value_avro_serializer)
            producer.produce(topic=params['TOPICO'], key=key, value=value)
            producer.flush()
        except Exception as e :
            print('>>> ERROR producing message to topic!')
            print('>>> {}'.format(e))
            exit(1)

    produce = True if input("Quer produzir outra mensagem ? (S/N) ") in ('S','s') else False
    
print('Done!')
print('#'*80)