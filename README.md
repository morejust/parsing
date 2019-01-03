# More Just Media Project 
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

A solution to analyze and evaluates texts, websites, articles...etc and give feedbacks and hints/advice...etc. It was built using natural language processing techniques and provides strong conclusions and evaluations for readers in order to detect the objective and good quality information from the bad one.<br>
The development of this project started during the 2018 edition of HackUPC hackathon.<br>

## Build and run
``` bash
docker build -t morejust_parsing:latest .
docker run -d -p 5000:80 morejust_parsing
```

## Other useful commands
``` bash 
docker ps
docker logs -ft <id>
docker tag <image_id> okhlopkov/morejust_parsing:latest
docker push okhlopkov/morejust_parsing:latest
```

## Links
Devpost : https://devpost.com/software/morejustmedia <br>
Website : https://morejust.media/ <br>
