# Template the sql logs according to the date
python sql_template.py --dir Raw_Logs/  --output_dir Templates

# Combine the templates
python combine_template.py --input_dir Templates/ --output_dir Combined_Templates/

# Online Clustering
python online_clustering.py --dir Combined_Templates/ --rho 0.8 --project SDSS

# Generate Clustering Coverage
python generate-cluster-coverage.py --project SDSS --similarity Euclid --assignment online-clustering-results/SDSS-0.8-assignments.pickle --output_csv_dir online-clusters/ --output_dir cluster-coverage/