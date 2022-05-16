trap 'kill $(jobs -p)' SIGINT SIGTERM EXIT

cd Webserver
npm start &
cd ..
python3 script/main.py