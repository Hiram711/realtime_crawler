# Realtime Crawler
## Install
1. Install redis
```bash
docker run -d -p 127.0.0.1:6179:6179 redis
docker ps -a 
```
*Take note the redis container info and write it in the app/config.py*
*Also don't forget to write your cookie pool host in the app/config.py*
  
2. Build the image 
```bash
git clone  docker https://github.com/Hiram711/realtime_crawler.git
cd realtime_crawler
docker build  . -t realtime_crawler:v1
```

3. Run
```bash
docker run -d -p 5020:5000 --name realtime_crawler --link your-redis-container realtime_crawler:v1
```

4. Notes
 
*if the cookie pool host is also built in docker in the same machine,you should use following ways to connect them*
 
*Also don't forget to write your cookie pool host in the app/config.py with a docker container name*
```bash
docker network create cookie2crawler
docker network connect cookie2crawler realtime_crawler
docker network connect cookie2crawler your_cookiepool_container
```