./run --config ./custom_configs/smallcorgi_exporter.yml --storage firebase --mode user
cp ./data_files_positives ~/accident_prediction_model/csvs
cp ./data_files_positives ~/accident_prediction_model/videos
cd ~/accident_prediction_model
python3 ./test/testFeatureGenerator.py
