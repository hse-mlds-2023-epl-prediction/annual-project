Если не созданы папки: mkdir -p ./dags ./logs ./plugins ./config 
Сохраните ваш AIRFLOW_UID для виртуальной машины в файл .env: echo -e "\nAIRFLOW_UID=$(id -u)" >> .env 
Затем запустите команду, которая создаст учётную запись с логином и паролем Airflow для веб-интерфейса: docker compose up airflow-init 
Очистка кэша: docker compose down --volumes --remove-orphans 
Запуск: docker compose up --build