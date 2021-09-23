#!/bin/bash

function sintaxe {
    echo ""
    echo "Script para auxiliar nas chamadas da rest interface do kafka-connect"
    echo "v1 - 09/2021 - Fernando Lino Di Tomazzo Silva - https://www.linkedin.com/in/flinox"
    echo ""
    echo "Parametros:"
    echo " <ip-kafka-connect>:<port>                 # ip e porta do kafka connect rest interface"
    echo ""    
    echo "Exemplo: ./kafka-connect-rest.sh localhost:8083"   
    echo ""   
 }

if [ -z "$1" ]; then
    sintaxe
    exit 1
else
  
    LOGLEVEL=""

    PS3='REST Interface for support: '
    options=("log level" "connectors" "plugins" "connector config" "connector status" "connector restart" "connector pause" "connector resume" "connector tasks" "connector task status" "connector task restart")
    select opt in "${options[@]}"
    do
        case $opt in
            "log level")
                
                while [[ $LOGLEVEL != @("OFF"|"FATAL"|"ERROR"|"WARN"|"INFO"|"DEBUG"|"TRACE") ]];
                do
                    read -p "  Informe o Level desejado (OFF,FATAL,ERROR,WARN,INFO,DEBUG,TRACE): " LOGLEVEL
                done

                curl -s -X PUT -H "Content-Type:application/json" \
                http://$1/admin/loggers/org.apache.kafka.connect.runtime.WorkerSourceTask \
                -d "{\"level\": \"$LOGLEVEL\"}" | jq '.'    
                
                break

                ;;

            "connector config")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/config | jq '.' 
                
                break

                ;;

            "connector status")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/status | jq '.' 
                
                break

                ;;            

            "connector restart")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X POST -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/restart | jq '.' 
                
                break

                ;;      


            "connector pause")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X PUT -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/pause | jq '.' 
                
                break

                ;;              
        
            "connector resume")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X PUT -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/resume | jq '.' 
                
                break

                ;;          

            "connector tasks")
                
                CONECTOR=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/tasks | jq '.' 
                
                break

                ;;     

            "connector task status")
                
                CONECTOR=""
                TASK=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                while [[ $TASK == @("") ]];
                do
                    read -p "  Informe o id da task: " TASK
                done            

                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/tasks/$TASK/status | jq '.' 
                
                break

                ;;    

            "connector task restart")
                
                CONECTOR=""
                TASK=""
                while [[ $CONECTOR == @("") ]];
                do
                    read -p "  Informe o nome do connector: " CONECTOR
                done

                while [[ $TASK == @("") ]];
                do
                    read -p "  Informe o id da task: " TASK
                done            

                curl -s -X POST -H "Content-Type:application/json" \
                http://$1/connectors/$CONECTOR/tasks/$TASK/restart | jq '.' 
                
                break

                ;;     

            "connectors")
                
                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connectors | jq '.' 
                
                break

                ;;        

            "plugins")
                
                curl -s -X GET -H "Content-Type:application/json" \
                http://$1/connector-plugins/ | jq '.' 
                
                break

                ;;                                               


            *) echo "opcao inválida $REPLY";;
        esac
    done



    echo ""
  


fi

;;


