#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para atualizar o timestamp para o momento de execução deste script (layout kafka-connect)"
    echo "a ideia é fazer com que o connector leia somente as atualizações a partir deste momento"
    echo "Atenção com o timezone antes de rodar esse script! requer kafka-cat / kcat e ccloud"
    echo ""
    echo "v1 - 09/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " <control_topic_name>                   # nome do tópico de controle Ex.: connect-offsets"
    echo " <connector_name>                       # nome do connector que deseja reinicializar o offset"    
    echo ""    
    echo "Exemplo: ./topic_update_offset.sh connect-offsets src-postgre-enem-score-requested"   
    echo ""   
 }

 function prop {
    grep "${1}" $PROPERTIES|cut -d'=' -f2
} 

if [ ! -z "$1" ] && [ ! -z "$2" ]; then

    export timeepoch=$(($(date +%s%N)/1000000))
    #echo $timeepoch

    export timemillis=$(echo $timeepoch | tail -c 4)
    #echo $timemillis

    export timemillisnano=$(echo $timemillis | sed -e :a -e 's/^.\{1,8\}$/&0/;ta')
    #echo $timemillisnano

    export timemillisnano=$(echo $timemillisnano | sed 's/^0*//')
    #echo $timemillisnano

read -p "O Topico [ $2 ] terá sua data de ultima leitura atualizada para epoch [ $timeepoch ] no tópico de controle [ $1 ] Confirma (S/N) ? " -n 1 -r

    case $REPLY in 
        s|S)

            echo ""
            echo '["'$2'",{"query":"query"}]|{"timestamp_nanos":'$timemillisnano',"timestamp":'$timeepoch'}'
            echo '["'$2'",{"query":"query"}]|{"timestamp_nanos":'$timemillisnano',"timestamp":'$timeepoch'}' | $kcat -t $1 -P -Z -K"|"

        ;;

        n|N)
            echo ""
            echo -e "Ok, nada foi feito, saindo..."
            exit 1
        ;;

        *)
            echo ""
            echo -e "Opção inválida, nada foi feito, saindo..."
            exit 1
        ;;
    esac

else
    sintaxe
    exit 1
fi
