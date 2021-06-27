
function sintaxe {
    echo ""
    echo "CONSUMER"
    echo "v1 - 05/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Configure o arquivo consumer.properties com os dados do seu ambiente ccloud"    
    echo ""
    echo "Parametros:"
    echo " <topic-name>        # Nome do topico"
    echo " <group-id>          # Grupo de consumo"
    echo " <time-out>          # Timeout em milisegundos - Default 60000"
    echo " <offset>            # earliest para desde o inicio - Default Latest"
    echo ""    
    echo "Exemplo: ./consumer.sh topic-name consumer1 90000 earliest"
    echo ""   
 }

function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

clear
PROPERTIES=../_keys/consumer.properties
TIMEOUT=60000
OFFSET=

if [ ! -z "$1" ] && [ ! -z "$2" ]; then

    if [ ! -z "$3" ]; then
        TIMEOUT=$3
    fi
    
    if [ ! -z "$4" ] && [ $4 == "earliest" ]; then
        OFFSET=--from-beginning
    fi

    kafka-console-consumer --bootstrap-server $(prop 'bootstrap.servers') \
    --topic $1 \
    --timeout-ms $TIMEOUT \
    --consumer.config $PROPERTIES \
    --property group.id=$2 \
    $OFFSET

else
    sintaxe
    exit 1
fi

