trap 'kill $(jobs -p)' SIGINT SIGTERM EXIT

cd Webserver
npm start &
cd ..
python3 -u script/main.py