
# Drip Car Bot


"Drip Car Bot" is a Telegram bot. It provides the ability to organize a system for exchanging video memes, their creation, and collecting statistics.

## Features

- Built-in flexible video constructor.
- Subscriptions - random car every day or/and new cars from past day.
- User-friendly search query.
- Likes, views statistic.




## Deployment

### Required for deployment:

- Telegram bot.
- Minio s3 bucket.
- Setup environment variables.

### Step-by-step:
1. Telegram bot:
    
Create your own telegram bot. Here's a [simple guide](https://core.telegram.org/bots/features#creating-a-new-bot).


2. Minio s3 bucket.
Create minio bucket. [MinIO Quickstart Guide](https://charts.min.io/).

Base bucket structure:
- bucket: *miniocars*
- folders: *cars_mp4*, *cars_mp3*
- files: *(car ID in database).mp4* for *cars_mp4*

Example full video path for car with id=236 in database:
```
miniocars/cars_mp4/236.mp4
```

You can change structure in *src/s3_client.py*.

3. Setup environment variables. 
  To run this project, you will need to change the following environment variables in *docker-compose.yml* file

`TOKEN` - your telegram bot token

`MINIO_ID` - set up your minio login 

`MINIO_KEY` - set up your minio password

`ADMIN_PASSWORD` - set up your password for using the bot's administrative functions.

After setting up the login and password for Minio, copy them into the following lines:

`MINIO_ROOT_USER` - your login for minio (`MINIO_ID`)

`MINIO_ROOT_PASSWORD` - your password for minio (`MINIO_KEY`)


### Deploy command 

First run (with building docker container):
```docker command
  docker-compose up --build
```

After first run:
```docker command
  docker-compose up
```

After run, your bot operates seamlessly without requiring any further configuration.

## Administration tools

To use admin tools, having an admin role is necessary, or alternatively, sending the password along with the command is required. All commands need to be sent in the bot's telegram chat.

Available commands:

- `give admin` - Grants admin role to a user by Telegram ID. Example:
```
give admin 123456789
```

- `send all` - sends the text entered after the command to all users. Example:
```
send all Hello world!
```

- `delete user` - removes a user from database by Telegram ID. Example:
```
delete user 123456789
```

- `delete car` - removes a car from the database and from the Minio storage. Example:
```
delete car 236
```
## License

Telegram Drip Car Bot is licensed under the MIT license that can be found in the [LICENSE](https://github.com/Pundanya/TG_DripcarBot/edit/main/LICENSE) file.

