#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para criação de schemas no schema registry na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " -f                 # para criar todos os schemas"
    echo " -s <schema_file>   # para criar somente o schema informado"
    echo ""    
    echo "Exemplo: ./create_schemas.sh -s account-created-key.json"   
    echo ""   
 }

function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

clear
PROPERTIES=../_keys/environment.properties
SCHEMAS_FOLDER=./schemas

SR_KEY=$(prop 'schemaregistry-username')
SR_SECRET=$(prop 'schemaregistry-password')
SR_HOST=$(prop 'schemaregistry-url')
AUTHORIZATION="$(echo -n $SR_KEY:$SR_SECRET | base64 -w 0)"

case $1 in

# Cria todos os schemas caso nao exista
-f)

    for i in $SCHEMAS_FOLDER/*.json; do 
        curl -i -s -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$(basename -s .json $i)/versions --data "$(jq -cr '. | tojson | { "schema" : select(.) , "schemaType": "AVRO" }' $i)"; 
    done

    ;;

# Cria somente um schema
-s)

    if [ -z "$2" ]; then
        sintaxe
        exit 1
    else
        curl -i -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" -H "Authorization: Basic $AUTHORIZATION" $SR_HOST/subjects/$(basename -s .json $2)/versions --data "$(jq -cr '. | tojson | {"schema":select(.)}' $SCHEMAS_FOLDER/$2)"
        echo ""
    fi
    ;;

# Não usou nenhum parametro valido
*)
    sintaxe
    exit 1
    ;;
esac

unset AUTHORIZATION
