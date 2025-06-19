
# Features

- User signup, login, and logout with JWT authentication
- Authenticated access to top headlines or searched news using NewsAPI
- Unauthenticated access to 5-day weather forecast using OpenWeatherMap
- Caching (in-memory) for improved performance
- Dockerized and ready to deploy
- Swagger documentation at `/docs`


# Step 1:
 -  git clone https://github.com/nehapanchal2606/New-Weather-API.


# step 2:
  - Create virtual environment 
  - Run the below command for the install necessary Library.
      - pip install -r requirements.txt
  - Add Your Secret token key and api from News and Weather

# step 3:
 - Run The main file using below command
    - uvicorn main:app --reload  (Use it when you have create .env file)
    - fastapi dev main.py (Use it when you direct pass key in the code)

# Run it with Docker
 - To create an docker image
    - docker build -t give-name .
 - To Run the docker 
    - docker run --env-file .env -p 8000:8000 data-hat-api

 click on sign up and add details 
    {
      "name": "admin",
      "email": "admin@gmail.com",
      "password": "admin"
    }

 Login
    username=admin@gmail.com
    password=admin

Response
   {
      "access_token": "<JWT_TOKEN>",
      "token_type": "bearer"
   }
Then click on "Authorize" and Use your credential to authorize

Go to the search about news 

Got ot the Check weather

Below i will provide the screen shot 

![Sign Up](https://github.com/user-attachments/assets/f670d60e-4a18-4b70-b7bc-aad62aa54da3)

![Success sign in](https://github.com/user-attachments/assets/7f2c9821-4596-482d-87fe-330992ffcfad)

![Login](https://github.com/user-attachments/assets/5f9d7a06-4929-42ef-8a46-cdfe93485fa7)

![Success login](https://github.com/user-attachments/assets/3f02c961-6701-492d-9ecf-612a7a103a9f)

![Authorize](https://github.com/user-attachments/assets/eb98d0ad-eb59-4aee-93c1-a0e84a7d0b66)

![Get Pune News](https://github.com/user-attachments/assets/88eb880d-9441-4387-8e7b-126bf5a98258)

![Get "Ahmedabad" Weather](https://github.com/user-attachments/assets/db2b5161-f7d4-4552-ad8c-a893d6e219dc)




