from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
import requests
from cachetools import TTLCache
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from jose import jwt

# Load environment variables
load_dotenv()

# App instance
app = FastAPI(title="API for get News & Weather")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
SECRET_KEY = os.getenv("SECRET_KEY", "my-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Auth and Cache
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
users_db = {}
blacklisted_tokens = set()
cache = TTLCache(maxsize=100, ttl=300)

# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    name: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class NewsItem(BaseModel):
    title: str
    description: Optional[str]
    url: str
    publishedAt: str

class WeatherItem(BaseModel):
    date: str
    main: str
    temp: float

class WeatherResponse(BaseModel):
    unit: str
    location: str
    data: List[WeatherItem]

# Call the simple root
@app.get("/")
def read_root():
    return {"message": "Welcome to the Data-Hat News & Weather API"}

def get_password_hash(password):
    return pwd_context.hash(password)

# verify the password
def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# create the access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# for the get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email or email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return users_db[email]
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Register the user
@app.post("/signup", response_model=User)
async def signup(user: UserCreate):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_db[user.email] = {
        "name": user.name,
        "email": user.email,
        "hashed_password": get_password_hash(user.password)
    }
    return {"name": user.name, "email": user.email}


# Login the user
@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

# Logoout
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return {"message": "Logged out successfully"}

# Generate the news response using api key
@app.get("/news")
async def get_news(search: Optional[str] = None, current_user: User = Depends(get_current_user)):
    cache_key = f"news_{search or 'top'}"
    if cache_key in cache:
        return {"count": len(cache[cache_key]), "data": cache[cache_key]}
    
    url = f"https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}&country=in"
    if search:
        url = f"https://newsapi.org/v2/everything?q={search}&apiKey={NEWS_API_KEY}"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="News API error")
    
    articles = response.json().get("articles", [])[:5]
    data = [
        NewsItem(
            title=a["title"],
            description=a.get("description"),
            url=a["url"],
            publishedAt=a["publishedAt"]
        ) for a in articles
    ]
    cache[cache_key] = data
    return {"count": len(data), "data": data}

# Generate the weather response by using weather api key
@app.get("/weather", response_model=WeatherResponse)
async def get_weather(location: str = "Bangalore", unit: str = "metric"):
    cache_key = f"weather_{location}_{unit}"
    if cache_key in cache:
        return WeatherResponse(**cache[cache_key])
    
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&units={unit}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather API error")
    
    forecast = response.json().get("list", [])[:5]
    weather_data = [
        WeatherItem(
            date=datetime.fromtimestamp(item["dt"]).strftime("%A, %d %B %Y"),
            main=item["weather"][0]["main"],
            temp=item["main"]["temp"]
        ) for item in forecast
    ]
    result = WeatherResponse(unit=unit, location=location, data=weather_data)
    cache[cache_key] = result.dict()
    return result