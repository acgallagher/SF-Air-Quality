# San Francisco Orange Week Air Quality Visualization

This project extracts air quality data from the PurpleAir API for the week of 9/9/2020 to 9/16/2020 - the week when San Francisco's sky turned orange. The goal of the project is to determine if, and to what extent, different neighborhoods experienced the wildfire smoke in different intensities.   

You can explore the interactive results on my Tableau Public profile [here](https://public.tableau.com/app/profile/andrew.gallagher5298/viz/SFOrangeWeek/SFOrangeWeekDashboard).

## Results

The findings show that while most neighborhoods display similar PM 2.5 air quality measurements, some neighborhoods are better than others. 

The best average air quality was found in:
- Noe Valley
- The Mission
- West Portal
- St Mary's Park
- Russian Hill

The worst average air quality was found in:
- Sunnyside
- Presidio Heights
- Bernal Heights
- Parnassus Heights
- SoMa

## Architecture

1. Configure Docker-Compose file to load Apache Airflow DAGs in locally run docker containers.
2. Enabled AWS S3 resources. 
3. Set up required Databricks serverless resources on AWS, including IAM access and EC2 resources. 
4. Orchestrate ETL with Airflow, including
    a. Extract from [PurpleAir API](https://api.purpleair.com/)
    b. Load to S3
    c. Transform in Databricks
5. Enable connection between Databricks and Tableau, and create/refresh visualizations. 

## Example Visualizations

![alt text](https://github.com/acgallagher/SF-Air-Quality/blob/main/images/map.png)

![alt text](https://github.com/acgallagher/SF-Air-Quality/blob/main/images/line%20chart.png)

![alt text](https://github.com/acgallagher/SF-Air-Quality/blob/main/images/bar%20chart.png)
