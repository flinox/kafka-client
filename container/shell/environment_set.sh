#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para configuração do ambiente de trabalho na confluent cloud"
    echo "v1 - 02/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo "v2 - 07/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"    
    echo ""
    echo "Exemplo:"    
    echo ". ./environment_set.sh"
    echo ""    
 }

 function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

case $1 in

  "/?" | "--help" | "-h")
        sintaxe
        exit 1
    ;;

   *)

        if [ ! -f "/app/_keys/env-dev.properties" ] || [ ! -f "/app/_keys/env-hml.properties" ]  ; then
            echo "Você não configurou seus arquivos com suas keys para os ambientes\nConsulte o README.md para mais informações!"
            exit 1
        fi
esac

clear
PS3='Escolha o ambiente CCLOUD que quer acessar: '
options=("DEV" "HML")
select opt in "${options[@]}"
do
    case $opt in
        "DEV")
            echo "Configurando para ambiente de DEV"
            export PROPERTIES=/app/_keys/env-dev.properties
            export KAFKACAT_CONFIG=/app/_keys/consumer-dev.properties
            break
            ;;
        "HML")
            echo "Configurando para ambiente de HML"
            export PROPERTIES=/app/_keys/env-hml.properties
            export KAFKACAT_CONFIG=/app/_keys/consumer-hml.properties
            break
            ;;
        *) echo "opcao inválida $REPLY";;
    esac
done

alias kafkacat-ccloud='kafkacat -b $(echo $(prop "kafka-broker") | sed s/"http[s]\?:\/\/"//) -X security.protocol=sasl_ssl -X sasl.mechanisms=PLAIN -X sasl.username=$(prop "kafka-username")  -X sasl.password=$(prop "kafka-password") -L'

cp /app/_keys/netrc ~/.netrc
chmod 600 ~/.netrc

ccloud environment use $(prop 'ccloud-environment')
ccloud kafka cluster use $(prop 'ccloud-cluster')
#ccloud api-key store $(prop 'schemaregistry-username') $(prop 'schemaregistry-password') --resource $(prop 'ccloud-cluster')
ccloud api-key store $(prop 'kafka-username') $(prop 'kafka-password') --resource $(prop 'ccloud-cluster')
ccloud api-key use $(prop 'kafka-username') --resource $(prop 'ccloud-cluster')

rm ~/.netrc